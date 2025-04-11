# Standard library imports
import logging
from datetime import datetime
import os
from random import random
from typing import Literal

# Third-party imports
from db import init_db
from dotenv import load_dotenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.pregel import RetryPolicy
import sqlitecloud
from vector_db import init_vectorstore

# Load environment variables from .env file
load_dotenv()

# Open the connection to SQLite Cloud
conn = sqlitecloud.connect(os.getenv('SQLITE_CLOUD_URL'))
# Initialize the database
init_db(conn)
conn.close()



# initialize the memory saver
memory = MemorySaver()

# Create an instance of LLM of your choice
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv('OPENAI_API_KEY'),
                      temperature=0)

# define our db as a set of sql tools
db = SQLDatabase.from_uri(os.getenv('SQLITE_CLOUD_URL'))
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = toolkit.get_tools()

# Connect LangChain with your Pinecone index
vectorstore = init_vectorstore()

# create a custom tool
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_docs = vectorstore.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

rag_tools = [retrieve]

# bind LLM with tools
llm_with_sql_tools = llm.bind_tools(tools=sql_tools)
llm_with_rag_tools = llm.bind_tools(tools=rag_tools)


# System message for conversational agent
sys_msg_conversation = SystemMessage(content="""

  Role: You are the Conversation Coordinator for a hotel chain’s customer
        support system. Your role is to manage the flow of the conversation
        with the guest and decide whether to handle the request yourself or
        forward the conversation to the next agent based on the user’s needs.

  Primary Tasks:

  Engage with the user: Start the conversation politely and ask
                                     how you can assist them.
  Identify the nature of the request: Listen to the guest’s inquiry and
    determine if it’s a general question, booking-related, issue resolution,
    or any other category that might require specialized handling.
  Route the conversation if necessary: If the request requires expertise
    outside your scope, forward it to a specialized agent by answering with
    the name of the corresponding agent.
  
    There are the following agents available:

  - reservation_assistant;
  - compliance_checker.

  Maintain a friendly and helpful tone: Always aim for a customer-friendly
    and empathetic response. Ensure the guest feels heard and cared for.

  Guidelines:

  - First you need to forward every query to compliance checker.
        If it violates any rule then do not respond, otherwise respond
        yourself or forward the query to the next agent.
  - For general inquiries (e.g., facilities, amenities, location details),
        assist the user directly.
  - If user wants to book a room. The following information: room type, 
        required dates. Only if user has provided this information forward
        to the reservation_assistant
        otherwise do not mention reservation_assistant.
   """)

# System message for sql-based reservation agent
sys_msg_sql = SystemMessage(content="""

  You are AI assistant specialized in SQL. You have access to the following
    database schema:

  Table: rooms
    room_number (INTEGER PRIMARY KEY)
    room_type (TEXT NOT NULL)
    price (REAL NOT NULL)
    max_capacity (INTEGER NOT NULL)
    amenities (TEXT)

  Table: reservations
    reservation_id (INTEGER PRIMARY KEY AUTOINCREMENT)
    guest_name (TEXT NOT NULL)
    room_number (INTEGER NOT NULL, FOREIGN KEY REFERENCES rooms(room_number))
    start_date (DATE NOT NULL)
    end_date (DATE NOT NULL)

  You must:
    Provide SQL queries or instructions referencing only these two tables
        and the columns defined above.
    Generate valid SQL statements that accurately address the user’s
        questions or requests.
    Include explanations about how the queries work or how they address
        the request.
    Use best practices for SQL (proper joins, filters, etc.).
    Do not reference any tables or columns other than rooms and reservations.
    If the user’s request is unclear or not possible with the given schema,
        ask for clarification or note the limitations.
    If user want to book a room check if the room is not already booked
        for the corresponding dates

   """)

# System message for rag-based compliance checker
sys_msg_rag = SystemMessage(content=f"""

  You are the Compliance Checker agent. Your role is to:
  - Understand the user’s request and determine which rules, regulations,
        or guidelines are relevant to the query.
  - Search a vector database (embedding-based document retrieval) to find
        the most pertinent guidelines or regulations that must be checked.

      You have read-only access to this vector database containing
        short texts, summaries, or entire regulations.
      You can pass a query (the user’s question, plus any relevant context)
        to retrieve the top related guidelines or rules.
  - Synthesize the results of your vector DB retrieval to provide a clear
        compliance assessment or recommendation.
      If the user’s question is ambiguous, incomplete,
        or requires additional detail to ensure compliance,
        politely request clarification.
      If no relevant guidelines can be found, state that no matching
        guidelines are found and ask the user if they have additional info.
  - Never fabricate guidelines. Only cite or summarize what is actually
        found in the vector database.
        If you cannot find relevant information, say so.


  Please follow these steps when generating a response:
    - you should not try to answer the request you should just check
            if it is compliant.
    - Retrieve the relevant guidelines from the vector DB using the
            user’s question or text as the query.
    - Summarize or quote the most critical points from those guidelines.
    - Provide your compliance assessment, specifying:
      Which guidelines apply
    - If you cannot find any rules to apply it means
        that the request is compliant.

    \n\n
        {0}

   """)

# Agent node
def conv_assistant(state: MessagesState) -> MessagesState:
   """
   SQL Assistant Agent

   Args:
     state (MessagesState): The current state of the conversation.

   Returns:
     MessagesState: The updated state of the conversation.
   """
   messages = state["messages"]
   return {"messages": [llm.invoke([sys_msg_conversation] + messages)]}

# SQL Agent node
def sql_assistant(state: MessagesState) -> MessagesState:
  """
   SQL Assistant Agent

   Args:
     state (MessagesState): The current state of the conversation.

   Returns:
     MessagesState: The updated state of the conversation.
   """
  messages = state["messages"]
  return {"messages": [llm_with_sql_tools.invoke([sys_msg_sql] + messages)]}

# RAG Agent node
def rag_assistant(state: MessagesState) -> MessagesState:
  """
   RAG Assistant Agent

   Args:
     state (MessagesState): The current state of the conversation.

   Returns:
     MessagesState: The updated state of the conversation.
   """
  messages = state["messages"]
  return {"messages": [llm_with_rag_tools.invoke([sys_msg_rag] + messages)]}

#
def generate(state: MessagesState) -> MessagesState:
    """
    Node for answer generation based on retrieved documents.

    Args:
      state (MessagesState): The current state of the conversation.

    Returns:
      MessagesState: The updated state of the conversation.
    """
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    docs_content = "\n\n".join(doc.content for doc in tool_messages)

    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]

    # Run
    response = llm.invoke([sys_msg_rag] + conversation_messages)
    return {"messages": [response]}

def choose_next_node(
    state: MessagesState
) -> Literal["reservation_assistant", "compliance_checker", "__end__"]:
    """Choose the next node based on the last message.

    Args:
        state (MessagesState): The current state of the conversation.

    Returns:
        str: The name of the next node.
    """
    last_message = state["messages"][-1]
    if ("reservation_assistant" in last_message.content or 
        "reservation assistant" in last_message.content):
        return "reservation_assistant"
    elif ("compliance_checker" in last_message.content or 
          "compliance checker" in last_message.content):
        return "compliance_checker"
    return "__end__"


# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("conv_assistant", conv_assistant)
builder.add_node("reservation_assistant", sql_assistant)
builder.add_node("compliance_checker", rag_assistant)
builder.add_node("retriever", generate)
builder.add_node("sql_tools", ToolNode(sql_tools))
builder.add_node("rag_tools", ToolNode(rag_tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "conv_assistant")
builder.add_conditional_edges(
    "conv_assistant",
    # If the message from assistant is a tool call -> routes to tools
    #Otherwise to the END
    choose_next_node, path_map=["reservation_assistant",
                                "compliance_checker", "__end__"])
builder.add_conditional_edges(
    "reservation_assistant",
    tools_condition,
    path_map={"tools": "sql_tools", "__end__": "__end__"})
builder.add_conditional_edges(
    "compliance_checker",
    tools_condition,
    path_map={"tools": "rag_tools", "__end__": "conv_assistant"})
builder.add_edge("sql_tools", "reservation_assistant")
builder.add_edge("rag_tools", "retriever")
builder.add_edge("retriever", "conv_assistant")
graph = builder.compile(checkpointer=memory)

thread_id = 42

def chat_with_agent(message, history):
  """
  Chat with the agent.

  Args:
    react_graph_with_memory (): The graph with the agent.
    thread_id (int): The ID of the thread.
  """
  events = graph.stream(
      input={"messages": [HumanMessage(content=message)]},
          config={"thread_id": thread_id},
          stream_mode="values",
  )

  for event in events:
      pass
  return event["messages"][-1].content

import gradio as gr

gr.ChatInterface(
    fn=chat_with_agent,
    type="messages"
).launch()
import gradio as gr
from langgraph_sdk import get_sync_client

def chat_with_agent(message, history) -> str:
  """
  Chat with the agent.

  """
  client = get_sync_client(url="http://langgraph-api:8000")

  thread = client.threads.create()

  for chunk in client.runs.stream(
    thread["thread_id"],
    "hotel_reservation_mas", # Name of assistant. Defined in langgraph.json.
    input={
        "messages": [{
            "role": "human",
            "content": message,
        }],
    },
    stream_mode="values",
  ):
    pass

  return chunk.data["messages"][-1]["content"]

gr.ChatInterface(
    fn=chat_with_agent,
    type="messages"
).launch(share=True, server_name="0.0.0.0", server_port=7860)
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

def init_vector_db(pc:Pinecone, index_name: str) -> PineconeVectorStore:
    """
    Initialize the vector database with compliance rules.
    
    Args:
        index_name (str): The name of the Pinecone index.
    
    Returns:
        vectorstore (PineconeVectorStore): The initialized vector store.
    """

    # Write compliance rules to the file and read it back
    with open('compliance.txt', 'w') as file:
        file.write('''The system should refuse
    or redirect queries with:''')
        file.write('''Illegal requests (e.g., falsifying documents,
    fraudulent bookings).''')
        file.write('''Hate speech, harassment, or explicit threats
    toward individuals or groups.''')
        file.write('''Offensive, obscene, or otherwise harmful content.''')
        file.write('''Request of information about other guests. You cannot
    share there names or dates of stay''')

    with open('compliance.txt', 'r') as file:
        content = file.read()

    dimension = 1536  # Dimension for text-embedding-ada-002
    pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            ) 
        )
    
    # Connect to the index
    index = pc.Index(index_name)

    # Set up OpenAI embeddings
    openai_embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )

    # Create Pinecone vector store with LangChain
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=openai_embeddings,
        text_key="text"  # The key used to store the text in the metadata
    )

    # Add documents to Pinecone
    vectorstore.add_texts(
        texts=[content],
        metadatas=[{"source": "compliance_rules"}],
        ids=["compliance_rules_1"]
    )

    return vectorstore


def init_vectorstore() -> PineconeVectorStore:
    """
    Initialize the vector store with compliance rules.
    
    Returns:
        vectorstore (PineconeVectorStore): The initialized vector store.
    """
        
    # Initialize Pinecone client
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))


    # Check if index exists, if not create it
    index_name = "compliance-rules"

    if index_name not in [x["name"] for x in pc.list_indexes()]:
        return init_vector_db(pc, index_name)
    else:
        # Connect to the index
        index = pc.Index(index_name)

        # Set up OpenAI embeddings
        openai_embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )

        # Create Pinecone vector store with LangChain
        vectorstore = PineconeVectorStore(
            index=index,
            embedding=openai_embeddings,
            text_key="text"  # The key used to store the text in the metadata
        )
        return vectorstore
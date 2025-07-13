from utils.pinecone_utils import process_pdf
from utils.openai_client import get_chat_completion
from utils.pinecone_utils import initialize_pinecone_index, get_embeddings_model
from typing import List, Dict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

@tool
def mem_search(query: str) -> List[Dict]:
    """
    **PRIMARY TOOL** for Master of Engineering Management (MEM) program information.
    
    Use this FIRST for any MEM-related queries before trying other tools.
    
    Covers:
    - MEM program structure, curriculum, specializations
    - MEM admissions requirements and process
    - MEM-specific faculty and courses
    - MEM career outcomes and industry connections
    
    **Use when:** Query mentions "MEM", "Master of Engineering Management", or "engineering management"
    **Don't use for:** General Pratt info, AIPI program, or non-MEM engineering programs
    
    Example: "What specializations does the MEM program offer?"
    """
    top_k = 3
    namespace = "mem-handbook"
    index_name = "mem-database"
    dimension = 1536
    metric = "cosine"
    
    embeddings = get_embeddings_model()
    if not embeddings:
        return "Error: Could not initialize embeddings model for MEM Search"
    
    # Create embedding for the query
    query_embedding = embeddings.embed_query(query)
    
    # Initialize index
    index = initialize_pinecone_index(index_name, dimension, metric, "MEM")
    
    # Search in Pinecone
    results = index.query(
        namespace=namespace,
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    return results

if __name__ == "__main__":

    pdf_path = "data/documents/MEM Student Handbook.pdf"
    namespace = "mem-handbook"
    
    # Process the PDF and create the database
    process_pdf(pdf_path, namespace)

    # delete_all_records(namespace)
    
    # Example search
    answer = mem_search("What is the graduation requirements for MEM program?")
    print(answer)


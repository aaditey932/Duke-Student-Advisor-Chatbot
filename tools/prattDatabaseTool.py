from utils.pinecone_utils import initialize_pinecone_index, get_embeddings_model
from utils.openai_client import get_chat_completion
from typing import List, Dict
from utils.pinecone_utils import process_pdf
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

@tool
def pratt_search(query: str) -> List[Dict]:
    """
    **GENERAL TOOL** for Pratt School of Engineering information (excluding MEM/AIPI specifics).
    
    Use for:
    - Overview of ALL Pratt engineering programs (MEng, MS, PhD)
    - General Pratt admissions, policies, facilities
    - Cross-program information and comparisons
    - Pratt-wide events, research centers, initiatives
    
    **Use when:** Query is about Pratt generally or non-MEM/AIPI engineering programs
    **Don't use for:** MEM-specific details (use mem_search) or AIPI-specific details (use get_AIPI_details)
    
    Example: "What engineering master's programs does Pratt offer?"
    """
    top_k = 3
    namespace = "pratt-handbook"
    index_name = "pratt-database"
    dimension = 1536
    metric = "cosine"
    
    embeddings = get_embeddings_model()
    if not embeddings:
        return "Error: Could not initialize embeddings model for Pratt Search"
    # Create embedding for the query
    query_embedding = embeddings.embed_query(query)
    
    # Initialize index
    index = initialize_pinecone_index(index_name, dimension, metric, "PRATT")
    
    # Search in Pinecone
    results = index.query(
        namespace=namespace,
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    system_prompt = "You are a helpful assistant that summarizes text."
    
    user_prompt = f"""Answer the following question based on the following text:
{results['matches']}

Question: {query}
"""
    
    messages = [SystemMessage(system_prompt),
            HumanMessage(user_prompt)]

    response = get_chat_completion(messages)
    
    if response is None:
        return "❌ Failed to get a valid response from OpenAI."
    answer = response.content
    
    return answer


if __name__ == "__main__":

    pdf_path = "data/documents/FINAL 24-25 BULLETIN Pratt Revised.pdf"
    namespace = "pratt-handbook"
    
    # Process the PDF and create the database
    process_pdf(pdf_path, namespace)

    # delete_all_records(namespace)
    
    # Example search
    answer = search("What program are offered at Pratt")
    print(answer)


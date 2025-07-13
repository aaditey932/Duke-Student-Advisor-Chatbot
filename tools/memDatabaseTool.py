from utils.pinecone_utils import process_pdf
from utils.openai_client import get_openai_client, get_chat_completion
from utils.pinecone_utils import initialize_pinecone_index, get_embeddings_model
from typing import List, Dict

def search(query: str) -> List[Dict]:
    """
    Search MEM related content in the vector database
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

    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes text."},
        {"role": "user", "content": f"""Answer the following question based on the following text:
{results['matches']}

Question: {query}
"""}
    ]

    response = get_chat_completion(messages)
    if response is None:
        return "Failed to get a valid response from OpenAI."
    answer = response.content
    
    return answer

if __name__ == "__main__":

    pdf_path = "data/documents/MEM Student Handbook.pdf"
    namespace = "mem-handbook"
    
    # Process the PDF and create the database
    process_pdf(pdf_path, namespace)

    # delete_all_records(namespace)
    
    # Example search
    answer = search("What is the graduation requirements for MEM program?")
    print(answer)


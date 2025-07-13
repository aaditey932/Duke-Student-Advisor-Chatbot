from utils.pinecone_utils import initialize_pinecone_index, get_embeddings_model
from utils.openai_client import get_openai_client, get_chat_completion
from typing import List, Dict
from utils.pinecone_utils import process_pdf

def search(query: str) -> List[Dict]:
    """
    Search Pratt related content in the vector database
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

    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes text."},
        {"role": "user", "content": f"""Answer the following question based on the following text:
{results['matches']}

Question: {query}
"""}
    ]

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


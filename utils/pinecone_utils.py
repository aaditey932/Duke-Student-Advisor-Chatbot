import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import math
from typing import List
import PyPDF2
from utils.openai_client import get_embeddings_model

# Load API Key
load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
# Initialize Pinecone client
pc = Pinecone(api_key=pinecone_api_key)


def initialize_pinecone_index(index_name, dimension, metric, db_name):
    """
    Creates or retrieves an existing Pinecone index and returns the index object.
    """
    existing_indexes = [index["name"] for index in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        print(f"Creating new Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=dimension,  # Model dimension
            metric=metric,        # Metric for similarity search
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )   

    # Get index details and print the host URL
    index_info = pc.describe_index(index_name)
    host_url = index_info['host']
    os.environ[f"PINECONE_INDEX_HOST_{db_name}"] = host_url

    print(f"Pinecone index host: {host_url}")

    # Connect to the index
    return pc.Index(index_name, host=host_url)


def upsert_vectors(index, vectors, batch_size, namespace=None):
    """
    Upserts vectors into the Pinecone index in batches, skipping if namespace already exists.
    """
    num_batches = math.ceil(len(vectors) / batch_size)
    
    for i in range(num_batches):
        batch = vectors[i * batch_size : (i + 1) * batch_size]
        index.upsert(vectors=batch, namespace=namespace)
        print(f"Upserted batch {i+1}/{num_batches}")

    print(f"Successfully upserted {len(vectors)} vectors into Pinecone!")


def process_pdf(pdf_path: str, namespace: str, index_name, dimension, metric, batch_size, api_key=None) -> None:
    """
    Process a PDF file, extract text page by page, create embeddings and store in Pinecone
    """
    if not api_key:
        return "Error: No API key provided for Pratt PDF processing"
    
    embeddings = get_embeddings_model(api_key)
    if not embeddings:
        return "Error: Could not initialize embeddings model for Pratt PDF processing"
    
    # Extract text from PDF page by page
    pages = _extract_text_from_pdf(pdf_path)
    
    # Create embeddings for each page
    vectors = []
    for page_num, page_text in enumerate(pages, start=1):
        # Split page text into chunks if needed
       
        embedding = embeddings.embed_query(page_text)
        vectors.append({
            'id': f"{namespace}-page{page_num}",
            'values': embedding,
            'metadata': {
                'text': page_text,
                'source': os.path.basename(pdf_path),
                'page_number': page_num,
                'pdf_path': pdf_path,
            }
        })
    
    # Store in Pinecone
    index = initialize_pinecone_index(index_name, dimension, metric)
    upsert_vectors(index, vectors, batch_size, namespace=namespace)

def _extract_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract text from a PDF file, returning a list of page texts
    """
    pages = []
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            pages.append(page.extract_text())
    return pages

def delete_all_records(index_name: str, dimension: int, metric: str, namespace: str):
    """
    Deletes all vectors from the specified namespace in the Pinecone index.
    """
    index = initialize_pinecone_index(index_name, dimension, metric)
    print(f"Deleting all vectors in namespace: '{namespace}'")
    
    index.delete(delete_all=True, namespace=namespace)
    
    print(f"All vectors deleted from namespace '{namespace}'.")


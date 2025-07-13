import os
import glob
from tqdm import tqdm
import uuid
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import time

# Load environment variables from .env file
load_dotenv()

def get_text_files(folder_path="scraped_websites"):
    """Get all text files from the specified folder."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist")
    
    # Get all .txt files in the folder
    file_paths = glob.glob(os.path.join(folder_path, "*.txt"))
    
    if not file_paths:
        raise ValueError(f"No text files found in '{folder_path}'")
    
    return file_paths

def read_text_file(file_path):
    """Read a text file and return its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def initialize_pinecone(api_key):
    """Initialize Pinecone client."""
    # Import here to avoid errors if the library isn't available
    from pinecone import Pinecone
    pc = Pinecone(api_key=api_key)
    return pc

def handle_index(pc, index_name, dimension=1536):
    """Handle Pinecone index creation or connection."""
    # Check if index exists
    existing_indexes = pc.list_indexes().names()
    
    if index_name not in existing_indexes:
        print(f"Index {index_name} doesn't exist. Please create it in the Pinecone dashboard first.")
        print("For free tier users, you should create the index manually in the Pinecone dashboard")
        print("with the following settings:")
        print(f"  - Name: {index_name}")
        print(f"  - Dimension: {dimension}")
        print("  - Metric: cosine")
        print("  - Use the default region for free tier")
        return None
    else:
        print(f"Using existing Pinecone index: {index_name}")
        return pc.Index(index_name)

def embed_and_store_documents(file_paths, embeddings_model, pinecone_index):
    """Embed documents and store in Pinecone."""
    # Keep track of processed files
    successful_uploads = 0
    failures = 0
    
    # Process each text file
    batch_size = 10  # Process in smaller batches to avoid rate limits
    
    for i in range(0, len(file_paths), batch_size):
        batch_files = file_paths[i:i+batch_size]
        vectors_batch = []
        
        for file_path in tqdm(batch_files, desc=f"Embedding batch {i//batch_size + 1}/{(len(file_paths)-1)//batch_size + 1}"):
            try:
                # Get file content
                content = read_text_file(file_path)
                if not content:
                    failures += 1
                    continue
                
                # Get file name (title) from the file path
                file_name = os.path.basename(file_path)
                title = os.path.splitext(file_name)[0]
                
                # Generate embedding
                embedding = embeddings_model.embed_query(content)
                
                # Create unique ID
                doc_id = str(uuid.uuid4())
                
                # Add to vectors batch
                vectors_batch.append({
                    "id": doc_id,
                    "values": embedding,
                    "metadata": {
                        "title": title,
                        "source": file_path
                    }
                })
                
                successful_uploads += 1
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                failures += 1
        
        # Upload batch to Pinecone
        if vectors_batch:
            try:
                pinecone_index.upsert(vectors=vectors_batch)
                print(f"Successfully uploaded batch {i//batch_size + 1} ({len(vectors_batch)} documents)")
                
                # Add a small delay between batches to avoid rate limits
                if i + batch_size < len(file_paths):
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"Error uploading batch to Pinecone: {e}")
                failures += len(vectors_batch)
                successful_uploads -= len(vectors_batch)
    
    return successful_uploads, failures

def main():
    # Check for required environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    
    if not all([openai_api_key, pinecone_api_key]):
        print("Missing required environment variables. Please check your .env file.")
        print("Required variables: OPENAI_API_KEY, PINECONE_API_KEY")
        return
    
    # Configuration
    embedding_model_name = "text-embedding-3-small"
    index_name = "meng-ai"
    
    # Get text files
    try:
        file_paths = get_text_files()
        print(f"Found {len(file_paths)} text files to process")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Initialize embedding model
    print(f"Initializing OpenAI embedding model: {embedding_model_name}")
    embeddings_model = OpenAIEmbeddings(model=embedding_model_name)
    
    # Initialize Pinecone
    print("Connecting to Pinecone...")
    pc = initialize_pinecone(pinecone_api_key)
    
    # Get Pinecone index
    pinecone_index = handle_index(pc, index_name)
    
    if pinecone_index:
        # Process files and store in Pinecone
        print("Processing files and storing in Pinecone...")
        successful, failed = embed_and_store_documents(file_paths, embeddings_model, pinecone_index)
        
        # Print results
        print(f"\nProcessing complete!")
        print(f"Successfully embedded and stored: {successful} files")
        print(f"Failed: {failed} files")
        print(f"Documents are stored in Pinecone index: {index_name}")
    else:
        print("\nPlease create the index manually in the Pinecone dashboard and run this script again.")

if __name__ == "__main__":
    main()
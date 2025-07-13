import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
import uuid

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Pinecone with the new API
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

# Connect to Pinecone index
index = pc.Index(os.getenv('PINECONE_INDEX'))

# Define the folder containing the text files
folder_path = "scraped_websites"

# Define a function to chunk text into smaller parts
def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Function to create embeddings
def create_embedding(text):
    response = client.embeddings.create(
        input=text,
        model=os.getenv('EMBEDDING_MODEL')
    )
    return response.data[0].embedding

# Iterate through all files in the folder
chunks_metadata = []
unique_id = 0

# Ensure the folder exists
if not os.path.exists(folder_path):
    print(f"Error: The folder '{folder_path}' does not exist.")
    exit(1)

# Process each text file
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)
        print(f"Processing file: {filename}")
        
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            chunks = chunk_text(text)
            
            # Process each chunk
            for position, chunk in enumerate(chunks):
                # Create a unique ID for this chunk
                chunk_id = str(unique_id)
                
                # Create metadata
                metadata = {
                    "text": chunk,
                    "position": position,
                    "source_file": filename,
                    "uniqueID": unique_id
                }
                
                # Create embedding
                embedding = create_embedding(chunk)
                
                # Upload to Pinecone
                index.upsert(
                    vectors=[(chunk_id, embedding, metadata)]
                )
                
                # Store metadata for verification
                chunks_metadata.append(metadata)
                
                unique_id += 1
                
                if unique_id % 10 == 0:
                    print(f"Processed {unique_id} chunks...")

print(f"Total chunks processed: {unique_id}")

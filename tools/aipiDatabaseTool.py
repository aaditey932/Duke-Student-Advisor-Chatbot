import os
import json
from typing import Dict, List, Any
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

class PineconeRetriever:
    def __init__(self, api_key=None, index_name=None, embedding_model="text-embedding-3-small"):
        """
        Initialize the PineconeRetriever with the necessary credentials.
        
        Args:
            api_key (str): Pinecone API key. Defaults to PINECONE_API_KEY env variable.
            index_name (str): Name of the Pinecone index. Defaults to PINECONE_INDEX env variable.
            embedding_model (str): OpenAI embedding model to use. Defaults to text-embedding-3-small.
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY_AIPI")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_AIPI")
        self.embedding_model = embedding_model
        
        if not all([self.api_key, self.index_name]):
            raise ValueError("Missing required Pinecone credentials")
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("Missing OpenAI API key")
        
        # Initialize Pinecone with new API
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.index_name)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.openai_api_key)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embeddings for a text using OpenAI's embedding model.
        
        Args:
            text (str): Text to embed
            
        Returns:
            List[float]: Vector embedding
        """
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding
    
    def query_and_reconstruct(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Main function to process a query, find similar vectors, and reconstruct files.
        
        Args:
            query (str): User query
            top_k (int): Number of top vectors to retrieve
            
        Returns:
            Dict: JSON response with reconstructed files
        """
        # Get embedding for the query
        query_embedding = self.get_embedding(query)
        
        # Query Pinecone for similar vectors
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Track unique source files from top results
        unique_source_files = set()
        for match in results['matches']:
            if 'metadata' in match and 'source_file' in match['metadata']:
                unique_source_files.add(match['metadata']['source_file'])
        
        reconstructed_files = []
        
        # Process each unique source file
        for source_file in unique_source_files:
            # Query to get all vectors from this source file
            file_query = {
                "source_file": {"$eq": source_file}
            }
            
            # Using a large top_k to ensure we get all chunks from the file
            file_vectors = self.index.query(
                vector=query_embedding,  # We still need a vector for the query
                filter=file_query,
                top_k=100,  # Assuming no single file has more than 100 chunks
                include_metadata=True
            )
            
            # Sort chunks by position to reconstruct the original text
            sorted_chunks = sorted(
                file_vectors['matches'], 
                key=lambda x: x['metadata'].get('position', 0) 
                if 'metadata' in x and 'position' in x['metadata'] else 0
            )
            
            # Reconstruct the full text
            reconstructed_text = ""
            for chunk in sorted_chunks:
                if 'metadata' in chunk and 'text' in chunk['metadata']:
                    reconstructed_text += chunk['metadata']['text'] + " "
            
            # Add to our results
            reconstructed_files.append({
                "source_file": source_file,
                "reconstructed_content": reconstructed_text.strip(),
                "relevance_score": next(
                    (m['score'] for m in results['matches'] 
                     if 'metadata' in m and m['metadata'].get('source_file') == source_file), 
                    0
                )
            })
        
        # Sort reconstructed files by relevance score (highest first)
        reconstructed_files.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            "query": query,
            "reconstructed_files": reconstructed_files
        }

@tool
def get_AIPI_details(query: str, api_key=None) -> Dict[str, Any]:
    """
    **PRIMARY TOOL** for Artificial Intelligence for Product Innovation (AIPI) program.
    
    **Use this FIRST** for any AIPI-related queries before other tools.
    
    Comprehensive coverage:
    - AIPI program overview, curriculum structure
    - AIPI admissions requirements and process  
    - AIPI faculty profiles and research areas
    - AIPI courses, projects, and career outcomes
    
    **Use when:** Query mentions "AIPI", "Artificial Intelligence for Product Innovation", or AI master's program
    **Also use get_courses("AIPI")** for detailed course listings
    
    Example: "Tell me about the AIPI program curriculum"
    """
    try:
        retriever = PineconeRetriever()
        result = retriever.query_and_reconstruct(query)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "reconstructed_files": []
        }

def main_json(query: str) -> str:
    """
    Similar to main(), but returns a JSON string instead of a dictionary.
    Useful when you need to return a JSON string directly.
    
    Args:
        query (str): User query
        
    Returns:
        str: JSON string with reconstructed files
    """
    result = main(query)
    return json.dumps(result, indent=2)

def test_with_chatgpt(query: str, context_data: Dict[str, Any] = None) -> None:
    """
    Test the retrieval tool with ChatGPT.
    
    Args:
        query (str): User query
        context_data (Dict): Optional - Already retrieved context data
    """
    # Get context from Pinecone if not provided
    if context_data is None:
        context_data = main(query)
    
    # Check if we have any reconstructed files
    if "error" in context_data or not context_data.get("reconstructed_files"):
        print("No relevant documents found or there was an error:")
        print(json.dumps(context_data, indent=2))
        return
    
    # Extract reconstructed content to use as context
    contexts = [file["reconstructed_content"] for file in context_data["reconstructed_files"]]
    context_text = "\n\n---\n\n".join(contexts)
    
    # Create prompt for ChatGPT
    prompt = f"""Use the following information to answer the question: "{query}"
    
Context information:
{context_text}

Answer:"""
    
    # Call ChatGPT to get the answer
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Use only the provided context information to answer the question."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Print the results
        print("\n=== Retrieved Context Files ===")
        for i, file in enumerate(context_data["reconstructed_files"], 1):
            print(f"{i}. {file['source_file']} (relevance: {file['relevance_score']:.3f})")
        
        # print("\n=== ChatGPT Response ===")
        # print(response.choices[0].message.content)
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling ChatGPT: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = input("Enter your query: ")
    
    print(f"Processing query: '{query}'")
    
    # Get the retrieval results (once)
    retrieval_results = get_AIPI_details(query)
    
    # # Show the raw retrieval results
    # print("\n=== Raw Retrieval Results ===")
    # print(json.dumps(retrieval_results, indent=2))
    
    # # Then, test with ChatGPT using the already retrieved results
    # print("\n=== Testing with ChatGPT ===")
    # test_with_chatgpt(query, retrieval_results)
    
    print("\n\n\n\n\n")
    print("=== ChatGPT Results===")
    print(retrieval_results)
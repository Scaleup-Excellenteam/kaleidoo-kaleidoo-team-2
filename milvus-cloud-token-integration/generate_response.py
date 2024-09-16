from pymilvus import connections, Collection
from text_embedding import embed_text
import openai  # Assuming you're using GPT-3.5 via OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI (or any other LLM service)
openai.api_key = os.getenv('OPENAI_API_KEY')

def connect_to_milvus_server():
    """
    Establishes a connection to the Milvus server using credentials from the environment variables.
    """
    public_endpoint = os.getenv('PUBLIC_ENDPOINT')
    token = os.getenv('TOKEN')
    
    connections.connect(
        alias="default", 
        uri=f"{public_endpoint}",  
        token=token  
    )
    print("Connected to Milvus Cloud!")

def search_embeddings(query):
    """
    Searches the Milvus collection for embeddings that are similar to the given query.
    
    Parameters:
    - query (str): Input query text to be embedded and searched.
    
    Returns:
    - A list of results with file paths and distances.
    """
    collection_name = "lecture_materials_embeddings"

    # Connect to Milvus and load the collection
    connect_to_milvus_server()
    collection = Collection(collection_name)
    collection.load()

    # Convert query text into embeddings
    query_embedding = embed_text(query)

    # Perform the search in Milvus
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(
        data=query_embedding,
        anns_field="embedding", 
        param=search_params,
        limit=5,  # Retrieve top 5 results
        output_fields=["file_path"]
    )

    # Fetch the file paths or content linked to the results
    retrieved_texts = []
    print(f"Search results for query '{query}':")
    for hits in results:
        for hit in hits:
            file_path = hit.entity.get('file_path')
            print(f"File Path: {file_path}, Distance: {hit.distance}")
            # For demonstration, assume file_path points to the actual text content
            # In practice, you'd load the text content from the file or database
            with open(file_path, 'r', encoding='utf-8') as f:
                retrieved_texts.append(f.read())

    return retrieved_texts

def generate_response(retrieved_texts, query):
    """
    Generate a coherent response based on the retrieved content using GPT.
    
    Parameters:
    - retrieved_texts (list of str): List of text contents retrieved from Milvus.
    - query (str): The original user query for context.

    Returns:
    - generated_text (str): The generated response text.
    """
    # Combine the retrieved texts
    combined_text = " ".join(retrieved_texts)
    
    # Use GPT-3 (or other models) to generate a response based on the combined text
    prompt = f"You are a helpful assistant. Answer the query: '{query}' based on the following content: {combined_text}"
    
    response = openai.Completion.create(
        engine="text-davinci-003",  # Use any relevant GPT model
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7
    )

    generated_text = response.choices[0].text.strip()
    return generated_text

if __name__ == "__main__":
    query = input("Enter the query text: ")
    try:
        # Search for relevant embeddings
        retrieved_texts = search_embeddings(query)
        
        if retrieved_texts:
            # Generate a response based on the retrieved content
            generated_response = generate_response(retrieved_texts, query)
            print(f"Generated Response: {generated_response}")
        else:
            print("No relevant results found.")
    
    except Exception as e:
        print(f"Error during search or generation: {e}")

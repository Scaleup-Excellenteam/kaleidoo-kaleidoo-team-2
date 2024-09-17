import asyncio
from search_embeddings import search_embeddings
from utils import get_openai_response

async def main():
    query = input("Enter the query text: ")
    
    try:
        # Search for relevant embeddings
        retrieved_data = search_embeddings(query)

        if retrieved_data:
            # Display the top 5 file paths and their distances
            print("\nTop 5 Results:")
            for idx, data in enumerate(retrieved_data, start=1):
                print(f"Result {idx}: File Path: {data['file_path']}, Distance: {data['distance']}")

            # Combine text content for OpenAI generation
            combined_texts = " ".join([data['text_content'] for data in retrieved_data])

            # Generate the response based on combined text
            response = get_openai_response(f"Answer the query: '{query}' based on the following content: {combined_texts}")
            
            # Display the generated response
            print("\nGenerated Response:")
            print(response)

        else:
            print("No relevant results found.")
    
    except Exception as e:
        print(f"Error during search or generation: {e}")

if __name__ == "__main__":
    asyncio.run(main())

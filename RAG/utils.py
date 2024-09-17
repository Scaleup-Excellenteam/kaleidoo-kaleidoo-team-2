from pymilvus import connections
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_to_milvus():
    """
    Connects to the Milvus server using credentials from environment variables.
    """
    public_endpoint = os.getenv('PUBLIC_ENDPOINT')
    token = os.getenv('TOKEN')
    connections.connect(
        alias="default",
        uri=f"{public_endpoint}",
        token=token
    )
    print("Connected to Milvus Cloud!")

def connect_to_openai():
    """
    Connects to OpenAI using credentials from environment variables.
    """
    openai.api_key = os.getenv('OPENAI_API_KEY')

def get_openai_response(prompt):
    """
    Sends a prompt to OpenAI's ChatCompletion API and returns the response.
    """
    connect_to_openai()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()

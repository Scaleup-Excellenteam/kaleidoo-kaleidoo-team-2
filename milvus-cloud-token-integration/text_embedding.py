from transformers import AutoTokenizer, AutoModel
import torch

# Load AlephBERT tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("onlplab/alephbert-base")
model = AutoModel.from_pretrained("onlplab/alephbert-base")

def embed_text(text):
    """
    Generates embeddings for a given input text using the AlephBERT model.

    Parameters:
    - text (str): The input text to be embedded.

    Returns:
    - embeddings (numpy.ndarray): A numpy array representing the text embeddings.
    """
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Extract embeddings from the [CLS] token (first token in the sequence)
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()
    return embeddings

if __name__ == "__main__":
    example_text = "Your Hebrew or English text here"
    embeddings = embed_text(example_text)
    print("Embeddings:", embeddings)

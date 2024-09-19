import torch
from FlagEmbedding import BGEM3FlagModel
import numpy as np


class EmbeddingModule:
    def __init__(self, use_gpu=True):

        self.device = torch.device("cuda" if torch.cuda.is_available() and use_gpu else "cpu")

        self.bgem3_model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True, device=self.device)

    def get_embedding(self, text, model='bgem3'):
        """
        Generate embeddings for the given text using the specified model.

        Args:
            text (str): The input text to embed.
            model (str): The model to use for embedding. Currently, only 'bgem3' is supported.

        Returns:
            numpy.ndarray: The embedding vector.

        Raises:
            ValueError: If an unsupported model is specified.
        """
        if model.lower() == 'bgem3':
            return self.bgem3_model.encode([text], batch_size=1, max_length=8192)['dense_vecs'][0]
        else:
            raise ValueError("Invalid model specified. Only 'bgem3' is currently supported.")

if __name__ == "__main__":
    embedder = EmbeddingModule()
    test_text = "This is a test sentence."
    bgem3_embedding = embedder.get_embedding(test_text, model='bgem3')
    print("BGEM3 embedding shape:", bgem3_embedding.shape)
from input_parsing import InputParsing
# from embedding import Embedding
# from vector_db import VectorDB
from minio_interface import MinIOInterface


class PipelineOrchestrator:
    def __init__(self, input_directory: str):
        """
        Initialize all components for orchestrating the pipeline.

        :param input_directory: The directory where input files are stored
        """
        self.minio = MinIOInterface(endpoint="localhost:9000", access_key="minioadmin", secret_key="minioadmin",
                                    bucket_name="mybucket")
        self.parser = InputParsing(input_directory, self.minio)
        # self.vector_db = VectorDB(host="localhost", port="19530")
        # self.embedding = Embedding(self.minio, self.vector_db)

    def run_parsing_pipeline(self):
        """
        Run the pipeline for parsing files from the input directory and saving them to MinIO.
        """
        self.parser.parse_files()

    # TODO Implement this side of the pipeline
    # def run_embedding_pipeline(self):
    #     """
    #     Run the pipeline for generating embeddings from new files stored in MinIO.
    #     """
    #     self.embedding.process_new_files()

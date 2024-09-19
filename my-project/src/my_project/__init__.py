from pipeline_orchestrator import PipelineOrchestrator

if __name__ == "__init__":
    # Specify the directory where input raw files are stored
    input_directory = "/path/to/input/files"

    # Initialize the pipeline orchestrator
    orchestrator = PipelineOrchestrator(input_directory)

    # Run the parsing pipeline to process files and store them in MinIO
    orchestrator.run_parsing_pipeline()

    # # Run the embedding pipeline to process new files from MinIO and store embeddings in VectorDB
    # orchestrator.run_embedding_pipeline()

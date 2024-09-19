import os
import time
from minio_client import MinIOClient

class AudioTextUploader:
    def __init__(self):
        self.minio_client = MinIOClient()

    def parse_audio_transcription(self, transcription_file):
        """
        Parses a transcription text file into a structured list of dictionaries.
        
        Args:
            transcription_file (str): The path to the transcription text file.
        
        Returns:
            list: A list of dictionaries, each containing start and end times and the transcription content.
        """
        transcription_content = []
        with open(transcription_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Loop over the lines two at a time (time range and transcription)
        for i in range(0, len(lines), 2):
            # Handle the time range and transcription
            time_range = lines[i].strip()
            transcription_text = lines[i+1].strip() if (i+1) < len(lines) else ""

            # Split the time range
            start_time, end_time = time_range.split('-')
            transcription_content.append({
                "start_time": start_time,
                "end_time": end_time,
                "content": transcription_text
            })
        
        return transcription_content

    def upload_audio_metadata(self, transcription_file):
        """
        Uploads the audio transcription metadata to MinIO.
        
        Args:
            transcription_file (str): The path to the transcription text file.
        """
        file_name_without_extension = os.path.basename(transcription_file).split('.')[0]
        
        # Parse the transcription into a structured format
        transcription_content = self.parse_audio_transcription(transcription_file)

        # Create the metadata dictionary
        audio_metadata = {
            "file_name": file_name_without_extension,
            "type": "audio",
            "transcription": transcription_content
        }

        # Upload the JSON metadata to MinIO
        object_name = f"{file_name_without_extension}_audio.json"
        self.minio_client.upload_json_to_minio("audio", object_name, audio_metadata)

    def run(self, transcription_file):
        """
        Main function to upload the transcription metadata.
        
        Args:
            transcription_file (str): The path to the transcription text file.
        """
        start_time = time.time()
        self.upload_audio_metadata(transcription_file)
        print(f"Time taken: {time.time() - start_time:.6f} seconds")

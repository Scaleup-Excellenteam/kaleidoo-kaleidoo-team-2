import os
import mimetypes

class InputParsing:
    def __init__(self, input_directory: str, minio_interface):
        """
        Initialize with the directory where input files are stored and MinIO interface.

        :param input_directory: The local directory where input files are stored
        :param minio_interface: An instance of the MinIOInterface for uploading parsed data
        """
        self.input_directory = input_directory
        self.minio_interface = minio_interface
        self.processed_files = set()  # Set to keep track of already processed files

    def parsing_audio_video(self, file_path) -> str:
        """
        Read and parse the audio or video file.
        :return the path of the processed file

        :param file_path: Path to the file to be parsed
        """
        pass  # TODO: Boris must implement this method

    def parsing_img_pdf(self, file_path) -> dict:
        """
        Read and parse the image or PDF file.

        :param file_path: Path to the file to be parsed
        :return: Parsed content as a dictionary
        """
        pass  # TODO: Ayham must implement this method

    def split_audio_video(self, file_path) -> list[dict]:
        """
        Split the audio or video file into smaller segments for json objects.

        :param file_path: Path to the audio or video file to be split
        :return: A list of dictionary objects, each containing a segment of the file
        """
        pass  # TODO: Ayham must implement this method

    def parse_files(self):
        """
        Continuously parse files in the input directory and save the parsed text in MinIO as JSON.
        The loop continues as long as there are unprocessed files.
        """
        while True:
            files = os.listdir(self.input_directory)

            # Get only the unprocessed files
            unprocessed_files = [f for f in files if f not in self.processed_files]

            # If no unprocessed files are found, break the loop
            if not unprocessed_files:
                print("All files have been processed. No new files found.")
                break

            for file_name in unprocessed_files:
                file_path = os.path.join(self.input_directory, file_name)
                file_type, _ = mimetypes.guess_type(file_path)

                if file_type is None:
                    print(f"File type of {file_name} could not be determined.")
                    continue

                if file_type == 'application/pdf' or file_type.startswith('image'):
                    dict_object = self.parsing_img_pdf(file_path)
                    self.minio_interface.upload_json(dict_object)

                elif file_type.startswith('audio') or file_type.startswith('video'):
                    processed_file_path = self.parsing_audio_video(file_path)
                    lst_dict_objects = self.split_audio_video(processed_file_path)
                    for dict_object in lst_dict_objects:
                        self.minio_interface.upload_json(dict_object)

                else:
                    print(f"File type {file_type} is not recognized.")
                    continue

                # Mark the file as processed
                self.processed_files.add(file_name)

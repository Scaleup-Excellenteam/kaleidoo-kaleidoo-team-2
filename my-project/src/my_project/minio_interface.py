from minio import Minio


class MinIOInterface:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str):
        """
        Initialize connection to MinIO.

        :param endpoint: MinIO server address
        :param access_key: MinIO access key
        :param secret_key: MinIO secret key
        :param bucket_name: MinIO bucket name where files will be stored
        """
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)
        self.bucket_name = bucket_name


    def upload_dict_object(self, dict_object):
        """
        Upload a dictionary object to MinIO as a JSON file.

        :param dict_object: The dictionary object to upload
        :param object_name: Name of the object (file) to upload to MinIO
        """
        pass # TODO: Ayham must implement this method


    def download_file(self, object_name: str) -> dict:
        """
        Download a file from MinIO.

        :param object_name: Name of the object (file) to download from MinIO
        :return: The content of the file as a string
        """
        pass #TODO Ayham must implement this method


    def list_files(self):
        """
        List all files stored in the MinIO bucket.
        We need it to Embedding module

        :return: A list of object names (file names) stored in the bucket
        """
        return [obj.object_name for obj in self.client.list_objects(self.bucket_name)]

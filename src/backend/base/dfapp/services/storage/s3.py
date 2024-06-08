import boto3  # type: ignore
from botocore.exceptions import ClientError, NoCredentialsError  # type: ignore
from loguru import logger

from .service import StorageService


class S3StorageService(StorageService):
    """A service class for handling operations with AWS S3 storage."""

    async def __init__(self, session_service, settings_service):
        """Initialize the S3 storage service with session and settings services."""
        super().__init__(session_service, settings_service)
        self.bucket = "dfapp"
        self.s3_client = boto3.client("s3")
        self.set_ready()

    async def save_file(self, folder: str, file_name: str, data):
        """
        Save a file to the S3 bucket.

        :param folder: The folder in the bucket to save the file.
        :param file_name: The name of the file to be saved.
        :param data: The byte content of the file.
        :raises Exception: If an error occurs during file saving.
        """
        try:
            self.s3_client.put_object(Bucket=self.bucket, Key=f"{folder}/{file_name}", Body=data)
            logger.info(f"File {file_name} saved successfully in folder {folder}.")
        except NoCredentialsError:
            logger.error("Credentials not available for AWS S3.")
            raise
        except ClientError as e:
            logger.error(f"Error saving file {file_name} in folder {folder}: {e}")
            raise

    async def get_file(self, folder: str, file_name: str):
        """
        Retrieve a file from the S3 bucket.

        :param folder: The folder in the bucket where the file is stored.
        :param file_name: The name of the file to be retrieved.
        :return: The byte content of the file.
        :raises Exception: If an error occurs during file retrieval.
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=f"{folder}/{file_name}")
            logger.info(f"File {file_name} retrieved successfully from folder {folder}.")
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Error retrieving file {file_name} from folder {folder}: {e}")
            raise

    async def list_files(self, folder: str):
        """
        List all files in a specified folder of the S3 bucket.

        :param folder: The folder in the bucket to list files from.
        :return: A list of file names.
        :raises Exception: If an error occurs during file listing.
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=folder)
            files = [item["Key"] for item in response.get("Contents", []) if "/" not in item["Key"][len(folder) :]]
            logger.info(f"{len(files)} files listed in folder {folder}.")
            return files
        except ClientError as e:
            logger.error(f"Error listing files in folder {folder}: {e}")
            raise

    async def delete_file(self, folder: str, file_name: str):
        """
        Delete a file from the S3 bucket.

        :param folder: The folder in the bucket where the file is stored.
        :param file_name: The name of the file to be deleted.
        :raises Exception: If an error occurs during file deletion.
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=f"{folder}/{file_name}")
            logger.info(f"File {file_name} deleted successfully from folder {folder}.")
        except ClientError as e:
            logger.error(f"Error deleting file {file_name} from folder {folder}: {e}")
            raise

    async def teardown(self):
        """Perform any cleanup operations when the service is being torn down."""
        # No specific teardown actions required for S3 storage at the moment.
        pass

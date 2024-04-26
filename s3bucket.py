import os

import boto3
from dotenv import load_dotenv

load_dotenv()


def upload_to_s3(file_path, file_name):
    ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    SECRET_KEY = os.getenv("AWS_SECRET_KEY")

    try:
        # Initialize a session using DigitalOcean Spaces.
        session = boto3.session.Session()
        client = session.client(
            "s3",
            region_name="ams3",
            endpoint_url="https://ams3.digitaloceanspaces.com",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )

        client.upload_file(Filename=file_path, Key=f"{file_name}", Bucket="adina-poc")
        return True

    except Exception as e:
        print("Error uploading file to S3 bucket.", e)
        return False

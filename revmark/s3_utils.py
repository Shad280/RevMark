import boto3
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class S3Manager:
    def __init__(self):
        self.s3_client = None
    
    def _get_client(self):
        """Get S3 client, initializing if needed"""
        if self.s3_client is None:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
                    region_name=current_app.config['AWS_REGION']
                )
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {str(e)}")
                self.s3_client = None
        return self.s3_client
    
    def upload_file(self, file, folder="uploads"):
        """
        Upload a file to S3 and return the S3 key and metadata
        
        Args:
            file: FileStorage object from Flask request
            folder: S3 folder prefix
            
        Returns:
            dict: Contains s3_key, original_filename, file_size, content_type
        """
        client = self._get_client()
        if not client:
            raise Exception("S3 client not initialized")
        
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        # Secure the filename and generate unique S3 key
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # Validate file extension
        allowed_extensions = current_app.config.get('UPLOAD_EXTENSIONS', [])
        if file_extension not in allowed_extensions:
            raise ValueError(f"File type {file_extension} not allowed")
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        s3_key = f"{folder}/{unique_filename}"
        
        # Get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        # Validate file size
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file_size > max_size:
            raise ValueError(f"File size exceeds maximum allowed size of {max_size} bytes")
        
        try:
            # Upload to S3
            client.upload_fileobj(
                file,
                current_app.config['AWS_S3_BUCKET'],
                s3_key,
                ExtraArgs={
                    'ACL': 'private',
                    'ContentType': file.content_type or 'application/octet-stream',
                    'Metadata': {
                        'original_filename': original_filename,
                        'upload_timestamp': str(int(os.time()))
                    }
                }
            )
            
            return {
                's3_key': s3_key,
                'original_filename': original_filename,
                'file_size': file_size,
                'content_type': file.content_type or 'application/octet-stream'
            }
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def generate_presigned_url(self, s3_key, expiration=3600):
        """
        Generate a presigned URL for accessing a file
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            str: Presigned URL
        """
        client = self._get_client()
        if not client:
            raise Exception("S3 client not initialized")
        
        try:
            url = client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': current_app.config['AWS_S3_BUCKET'],
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    def delete_file(self, s3_key):
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            bool: True if successful
        """
        client = self._get_client()
        if not client:
            raise Exception("S3 client not initialized")
        
        try:
            client.delete_object(
                Bucket=current_app.config['AWS_S3_BUCKET'],
                Key=s3_key
            )
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            return False
    
    def get_file_info(self, s3_key):
        """
        Get metadata about a file in S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            dict: File metadata
        """
        if not self.s3_client:
            raise Exception("S3 client not initialized")
        
        try:
            response = self._get_client().head_object(
                Bucket=current_app.config['AWS_S3_BUCKET'],
                Key=s3_key
            )
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response['ContentType'],
                'metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            logger.error(f"Failed to get file info: {str(e)}")
            return None

# Initialize global S3 manager instance
s3_manager = S3Manager()
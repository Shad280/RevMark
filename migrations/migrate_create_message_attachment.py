"""
Migration script to create the message_attachment table.
"""
from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, MetaData
from sqlalchemy import create_engine
import os

DATABASE_URL = "postgresql://postgres:CAxURJFzItKFLjAvOnIdmeJltIYtclRW@yamabiko.proxy.rlwy.net:50386/railway"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

message_attachment = Table(
    "message_attachment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("message_id", Integer, ForeignKey("message.id")),
    Column("filename", String(255)),
    Column("original_filename", String(255)),
    Column("s3_key", String(255)),
    Column("file_size", Integer),
    Column("content_type", String(128)),
    Column("timestamp", DateTime),
)

def run_migration():
    message_attachment.create(bind=engine)
    print("message_attachment table created.")

if __name__ == "__main__":
    run_migration()

"""Document model"""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, JSON
from datetime import datetime
from app.database import Base


class Document(Base):
    """Document model for document management"""

    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)

    # Document Details
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, xlsx, etc.
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes

    # Categorization
    category = Column(String, nullable=True, index=True)  # report, presentation, contract, etc.
    tags = Column(JSON, default=list)

    # Ownership
    owner_id = Column(String, nullable=True)
    created_by = Column(String, default="tammy")
    department = Column(String, nullable=True)

    # Access Control
    is_public = Column(Boolean, default=False)
    shared_with = Column(JSON, default=list)  # List of user IDs
    access_level = Column(String, default="private")  # private, shared, public

    # Versioning
    version = Column(String, default="1.0")
    previous_version_id = Column(String, nullable=True)
    is_latest_version = Column(Boolean, default=True)

    # Status
    status = Column(String, default="active")  # active, archived, deleted

    # Content Extraction (for searchability)
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    keywords = Column(JSON, default=list)

    # Metadata
    download_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # External Storage
    storage_provider = Column(String, default="local")  # local, s3, google_drive, etc.
    external_url = Column(String, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Document {self.title} [{self.file_type}]>"

"""Contact model"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Contact(Base):
    """Contact model for relationship management"""

    __tablename__ = "contacts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Basic Information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    full_name = Column(String, nullable=False, index=True)
    nickname = Column(String, nullable=True)

    # Contact Details
    email = Column(String, nullable=True, index=True)
    phone_number = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
    company = Column(String, nullable=True, index=True)
    job_title = Column(String, nullable=True)
    department = Column(String, nullable=True)

    # Address
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)

    # Important Dates
    birthday = Column(Date, nullable=True)
    anniversary = Column(Date, nullable=True)

    # Social & Web
    linkedin_url = Column(String, nullable=True)
    twitter_handle = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # Relationship
    relationship_type = Column(String, nullable=True)  # client, colleague, vendor, friend, etc.
    priority = Column(String, default="normal")  # high, normal, low

    # Notes and Tags
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)

    # Custom Fields
    custom_fields = Column(JSON, default=dict)

    # Metadata
    is_favorite = Column(Boolean, default=False)
    last_contacted = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="contacts")

    def __repr__(self):
        return f"<Contact {self.full_name}>"

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, LargeBinary, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # HTML description
    author = Column(String(200), nullable=False, index=True)
    announce_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # relationships
    attachments = relationship("Attachment", back_populates="post", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="post", cascade="all, delete-orphan")
    views = relationship("PostView", back_populates="post", cascade="all, delete-orphan")
    replies = relationship("Reply", back_populates="post", cascade="all, delete-orphan")
    shares = relationship("Share", back_populates="post", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "post_attachments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(120), nullable=False)
    size = Column(Integer, nullable=False)
    is_image = Column(Boolean, default=False)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    post = relationship("Post", back_populates="attachments")


class Reaction(Base):
    __tablename__ = "post_reactions"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user = Column(String(200), nullable=False)
    reaction = Column(String(50), nullable=False)  # like, love, etc.
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    post = relationship("Post", back_populates="reactions")


class PostView(Base):
    __tablename__ = "post_views"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user = Column(String(200), nullable=False)
    viewed_at = Column(DateTime, nullable=False, server_default=func.now())

    post = relationship("Post", back_populates="views")


class Reply(Base):
    __tablename__ = "post_replies"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    post = relationship("Post", back_populates="replies")


class Share(Base):
    __tablename__ = "post_shares"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user = Column(String(200), nullable=False)
    platform = Column(String(120), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    post = relationship("Post", back_populates="shares")

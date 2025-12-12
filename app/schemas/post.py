from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AttachmentMeta(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    is_image: bool
    created_at: datetime
    class Config:
        orm_mode = True


class ReactionSchema(BaseModel):
    id: int
    user: str
    reaction: str
    created_at: datetime
    class Config:
        orm_mode = True


class ReplySchema(BaseModel):
    id: int
    user: str
    content: str
    created_at: datetime
    class Config:
        orm_mode = True


class ShareSchema(BaseModel):
    id: int
    user: str
    platform: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: str
    description: Optional[str] = None
    author: str
    announce_type: Optional[str] = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    announce_type: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    author: str
    announce_type: Optional[str]
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentMeta] = []
    reactions: List[ReactionSchema] = []
    views_count: int = 0
    replies_count: int = 0
    shares_count: int = 0
    liked_users: List[str] = []
    class Config:
        orm_mode = True


class PostListResponse(BaseModel):
    total: int
    posts: List[PostResponse]
    class Config:
        orm_mode = True

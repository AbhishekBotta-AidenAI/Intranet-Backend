from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.post import Post, Attachment, Reaction, PostView
from app.schemas.post import PostCreate, PostResponse, PostListResponse, PostUpdate, AttachmentMeta, ReactionSchema, ReplySchema, ShareSchema
from app.models.post import Reply, Share
from fastapi.responses import Response

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    author: str = Form(...),
    announce_type: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
):
    """Create a post with optional attachments (multipart/form-data). Files are stored in DB."""
    post = Post(title=title, description=description, author=author, announce_type=announce_type)
    db.add(post)
    db.commit()
    db.refresh(post)

    # handle files
    if files:
        for f in files:
            content = await f.read()
            att = Attachment(
                post_id=post.id,
                filename=f.filename,
                content_type=f.content_type or 'application/octet-stream',
                size=len(content),
                is_image=(f.content_type or '').startswith('image/'),
                data=content,
            )
            db.add(att)
        db.commit()

    # eager load relations
    db.refresh(post)
    # compute views_count
    views_count = db.query(PostView).filter(PostView.post_id == post.id).count()

    return PostResponse(
        id=post.id,
        title=post.title,
        description=post.description,
        author=post.author,
        announce_type=post.announce_type,
        created_at=post.created_at,
        updated_at=post.updated_at,
        attachments=[AttachmentMeta.from_orm(a) for a in post.attachments],
        reactions=[],
        views_count=views_count,
    )


@router.get("/", response_model=PostListResponse)
def list_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    q = db.query(Post).order_by(Post.created_at.desc())
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    posts_out = []
    for p in items:
        views_count = db.query(PostView).filter(PostView.post_id == p.id).count()
        replies_count = db.query(Reply).filter(Reply.post_id == p.id).count()
        shares_count = db.query(Share).filter(Share.post_id == p.id).count()
        # collect usernames who reacted with 'like'
        liked_users = [r.user for r in p.reactions if (r.reaction or '').lower() == 'like']
        posts_out.append(PostResponse(
            id=p.id,
            title=p.title,
            description=p.description,
            author=p.author,
            announce_type=p.announce_type,
            created_at=p.created_at,
            updated_at=p.updated_at,
            attachments=[AttachmentMeta.from_orm(a) for a in p.attachments],
            reactions=[ReactionSchema.from_orm(r) for r in p.reactions],
            views_count=views_count,
            replies_count=replies_count,
            shares_count=shares_count,
            liked_users=liked_users,
        ))

    return PostListResponse(total=total, posts=posts_out)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    views_count = db.query(PostView).filter(PostView.post_id == p.id).count()
    return PostResponse(
        id=p.id,
        title=p.title,
        description=p.description,
        author=p.author,
        announce_type=p.announce_type,
        created_at=p.created_at,
        updated_at=p.updated_at,
        attachments=[AttachmentMeta.from_orm(a) for a in p.attachments],
        reactions=[ReactionSchema.from_orm(r) for r in p.reactions],
        views_count=views_count,
        replies_count=db.query(Reply).filter(Reply.post_id == p.id).count(),
        shares_count=db.query(Share).filter(Share.post_id == p.id).count(),
        liked_users=[r.user for r in p.reactions if (r.reaction or '').lower() == 'like'],
    )


@router.get("/{post_id}/attachments/{att_id}")
def get_attachment(post_id: int, att_id: int, db: Session = Depends(get_db)):
    att = db.query(Attachment).filter(Attachment.id == att_id, Attachment.post_id == post_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return Response(content=att.data, media_type=att.content_type, headers={"Content-Disposition": f"inline; filename=\"{att.filename}\""})


@router.get("/{post_id}/replies", response_model=List[ReplySchema])
def list_replies(post_id: int, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    return [ReplySchema.from_orm(r) for r in p.replies]


@router.post("/{post_id}/replies", response_model=ReplySchema, status_code=status.HTTP_201_CREATED)
def add_reply(post_id: int, user: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    r = Reply(post_id=post_id, user=user, content=content)
    db.add(r)
    db.commit()
    db.refresh(r)
    return ReplySchema.from_orm(r)


@router.post("/{post_id}/shares", response_model=ShareSchema, status_code=status.HTTP_201_CREATED)
def add_share(post_id: int, user: str = Form(...), platform: Optional[str] = Form(None), db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    s = Share(post_id=post_id, user=user, platform=platform)
    db.add(s)
    db.commit()
    db.refresh(s)
    return ShareSchema.from_orm(s)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    announce_type: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    if title is not None:
        p.title = title
    if description is not None:
        p.description = description
    if announce_type is not None:
        p.announce_type = announce_type
    db.add(p)
    db.commit()
    # add files if provided
    if files:
        for f in files:
            content = await f.read()
            att = Attachment(
                post_id=p.id,
                filename=f.filename,
                content_type=f.content_type or 'application/octet-stream',
                size=len(content),
                is_image=(f.content_type or '').startswith('image/'),
                data=content,
            )
            db.add(att)
        db.commit()
    db.refresh(p)
    views_count = db.query(PostView).filter(PostView.post_id == p.id).count()
    return PostResponse(
        id=p.id,
        title=p.title,
        description=p.description,
        author=p.author,
        announce_type=p.announce_type,
        created_at=p.created_at,
        updated_at=p.updated_at,
        attachments=[AttachmentMeta.from_orm(a) for a in p.attachments],
        reactions=[ReactionSchema.from_orm(r) for r in p.reactions],
        views_count=views_count,
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(p)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{post_id}/reactions", response_model=ReactionSchema, status_code=status.HTTP_201_CREATED)
def add_reaction(post_id: int, user: str = Form(...), reaction: str = Form(...), db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    r = Reaction(post_id=post_id, user=user, reaction=reaction)
    db.add(r)
    db.commit()
    db.refresh(r)
    return ReactionSchema.from_orm(r)


@router.post("/{post_id}/views", status_code=status.HTTP_201_CREATED)
def add_view(post_id: int, user: str = Form(...), db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    v = PostView(post_id=post_id, user=user)
    db.add(v)
    db.commit()
    return {"status": "ok"}

from fastapi import FastAPI

# Minimal Vercel entrypoint: do NOT import `app.main` here.
# This file must define `app` and avoid indirect imports that pull in
# vendored packages before Vercel installs requirements.

from app.routes.posts import router as posts_router
from app.routes.documents import router as documents_router

app = FastAPI(title="Intranet API (Vercel)")

# Include routers from the app package
app.include_router(posts_router)
app.include_router(documents_router)


@app.get("/")
def _root():
	return {"status": "running"}


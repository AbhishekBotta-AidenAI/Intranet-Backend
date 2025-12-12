from app.main import app

# Vercel looks for a variable named `app` in `api/main.py`.
# We import the FastAPI instance from `app.main` so the existing
# application (routes, middleware, DB setup) is exposed to Vercel.

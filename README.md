# Intranet Backend API

FastAPI backend for HR Policies Management with PostgreSQL

## Setup Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL installed and running
- UV package manager

### Installation

1. **Install UV** (if not already installed):
```bash
pip install uv
```

2. **Create .env file** from example:
```bash
cp .env.example .env
```

3. **Edit .env file** with your database credentials:
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/intranet
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
```

4. **Create PostgreSQL database**:
```sql
CREATE DATABASE intranet;
```

5. **Sync dependencies with UV**:
```bash
uv sync
```

### Running the Application

1. **Start the server**:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Access the API**:
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## API Endpoints

### Documents

- **POST** `/api/documents` - Create a new document
- **GET** `/api/documents` - Get all documents (with pagination)
- **GET** `/api/documents/{id}` - Get specific document
- **PUT** `/api/documents/{id}` - Update a document
- **DELETE** `/api/documents/{id}` - Delete a document
- **GET** `/api/documents/{id}/link` - Get SharePoint link

## Request/Response Examples

### Create Document
```json
POST /api/documents

{
  "name": "Employee Handbook",
  "description": "Company policy for all employees",
  "link": "https://sharepoint.com/sites/hr/documents/handbook.pdf"
}
```

### Get Documents
```
GET /api/documents?skip=0&limit=10
```

## Database Schema

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    link VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables

```
DATABASE_URL=postgresql://user:password@localhost:5432/intranet
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=intranet
DATABASE_USER=postgres
DATABASE_PASSWORD=password
APP_NAME=Intranet API
APP_DEBUG=True
APP_PORT=8000
APP_HOST=0.0.0.0
ALLOWED_ORIGINS=http://localhost:5174,http://localhost:3000
```

## Technologies Used

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Database
- **Pydantic** - Data validation
- **UV** - Python package manager
- **Uvicorn** - ASGI server
- **python-decouple** - Configuration management

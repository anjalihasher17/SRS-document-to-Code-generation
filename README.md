# SRS to FastAPI Generator

A system that takes Software Requirements Specification (SRS) documents as input and automatically generates complete FastAPI projects.

## Overview

The SRS to FastAPI Generator is an AI-powered tool that automates the process of converting Software Requirements Specification (SRS) documents into fully functional FastAPI applications. By leveraging Large Language Models (LLMs) through LangChain and LangGraph, the system analyzes SRS documents, extracts key requirements, and generates a structured FastAPI project with database models, API endpoints, and business logic implementations.

## Features

- **SRS Document Processing**: Upload and process .docx SRS documents
- **Automated Analysis**: Extract API endpoints, database schema, business logic, and authentication requirements
- **Project Generation**: Create a complete FastAPI project structure with:
  - SQLAlchemy database models
  - FastAPI routes and endpoints
  - Authentication and authorization
  - Configuration files (Dockerfile, docker-compose.yml, etc.)
  - Documentation
- **LangSmith Integration**: Track and monitor the generation process with LangSmith

## System Architecture

The system uses a workflow-based approach with LangGraph to process SRS documents:

1. **Document Parsing**: Extract text content from .docx files
2. **Requirements Analysis**: Use LLMs to identify API endpoints, database schema, business logic, and auth requirements
3. **Project Structure Generation**: Create directories and files for the FastAPI project
4. **Code Generation**: Generate Python code for models, routes, and services
5. **Configuration Generation**: Create necessary configuration files
6. **Documentation Generation**: Create API and workflow documentation

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL (optional, SQLite can be used for testing)

### Setup

1. Clone the repository:
   ```bash
   git clone git clone https://github.com/anjalihasher17/srs-to-fastapi.git
   cd srs-to-fastapi
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```
   # LLM API Keys
   GROQ_API_KEY=your_groq_api_key
   
   # Database
   DATABASE_URL=sqlite+aiosqlite:///./test.db
   # For PostgreSQL: postgresql://user:password@localhost:5432/dbname
   ```

## Usage

### Running the API Server

Start the FastAPI server:

```bash
cd app
uvicorn main:app --reload
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs.

### Processing an SRS Document

1. Prepare your SRS document in .docx format
2. Use the API endpoint to upload and process the document:
   ```bash
   curl -X POST "http://localhost:8000/api/srs/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/your/srs.docx"
   ```
3. You'll receive a job ID that you can use to check the status:
   ```bash
   curl "http://localhost:8000/api/srs/status/{job_id}"
   ```
4. Once processing is complete, you can access the generated project:
   ```bash
   curl "http://localhost:8000/api/srs/project/{project_id}"
   ```

## Project Structure

```
project-srs/
├── app/                      # Main application directory
│   ├── api/                  # API endpoints
│   │   └── routes/           # Route definitions
│   │       ├── __init__.py
│   │       └── srs.py        # SRS processing routes
│   ├── generated_projects/   # Output directory for generated projects
│   ├── services/             # Service layer
│   │   ├── __init__.py
│   │   └── database.py       # Database connection handling
│   ├── uploads/              # Directory for uploaded SRS documents
│   └── main.py               # FastAPI application entry point
├── workflow/                 # LangGraph workflow
│   └── workflow.py           # Workflow definition
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## Generated Project Structure

Each generated project follows a standard FastAPI structure:

```
generated_project/
├── app/
│   ├── api/
│   │   ├── routes/           # Generated API routes
│   │   └── __init__.py
│   ├── models/               # SQLAlchemy models
│   │   └── ...
│   ├── services/             # Service layer
│   │   └── database.py
│   ├── __init__.py
│   └── main.py               # FastAPI application
├── docs/                     # Documentation
│   ├── api.md
│   └── workflow.md
├── tests/                    # Test directory
├── .env.example              # Environment variables example
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **LangChain**: Framework for developing applications powered by language models
- **LangGraph**: Framework for building stateful, multi-actor applications with LLMs
- **Groq/LLama**: LLM provider for text generation
- **Python-DOCX**: Library for processing Word documents
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for FastAPI

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://www.langchain.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [SQLAlchemy](https://www.sqlalchemy.org/)#

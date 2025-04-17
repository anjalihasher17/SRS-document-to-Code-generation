
import os
import uuid
import json
import docx2txt
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import Document
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.schema.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from typing import Annotated
from langchain_core.messages import AnyMessage
import re

class GraphState(BaseModel):

    srs_document: Optional[str] = None
    srs_path: Optional[str] = None
    

    api_endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    database_schema: List[Dict[str, Any]] = Field(default_factory=list)
    business_logic: List[Dict[str, Any]] = Field(default_factory=list)
    auth_requirements: Dict[str, Any] = Field(default_factory=dict)
    
    project_id: Optional[str] = None
    project_path: Optional[str] = None
    generated_files: List[Dict[str, str]] = Field(default_factory=list)
    test_results: List[Dict[str, Any]] = Field(default_factory=list)
    
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "initialized"
    langsmith_trace_url: Optional[str] = None
    
    messages: Annotated[list, add_messages] = Field(default_factory=list)

    # Validation and regeneration
    validation_results: Dict[str, Any] = Field(default_factory=dict)
    regeneration_count: int = 0
    max_regenerations: int = 3
    regeneration_target: Optional[str] = None


def get_llm(temperature=0.2):
    return ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key="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")


def parse_srs_document(state: GraphState) -> GraphState:
    if state.srs_path:
        file_ext = os.path.splitext(state.srs_path)[1].lower()
        
        if file_ext != ".docx":
            raise ValueError("Only .docx files are supported for parsing.")

        try:
            text = docx2txt.process(state.srs_path)
            state.srs_document = text

            state.messages.append({
                "role": "system",
                "content": f"Parsed SRS document: {len(text)} characters"
            })
        except Exception as e:
            raise ValueError(f"Failed to parse .docx file: {e}")
    return state



async def process_srs_document(file_path: str) -> Tuple[str, Optional[str]]:

    workflow = create_workflow()
    state = GraphState(srs_path=file_path)
    result = await workflow.ainvoke(state)
    return result["project_id"], result.get("langsmith_trace_url")


def analyze_requirements(state: GraphState) -> GraphState:
    if not state.srs_document:
        state.messages.append({
                "role": "user",
                "content": "Error: No SRS document to analyze"
            })

        state.status = "failed"
        return state
    llm = get_llm()
    
    api_prompt = PromptTemplate.from_template(
        """
        You are a requirements analyst specializing in API design.
        
        Analyze the following Software Requirements Specification (SRS) document and extract all API endpoints that need to be implemented.
        
        For each endpoint, identify:
        1. The HTTP method (GET, POST, PUT, DELETE, etc.)
        2. The route path
        3. Request parameters and their types
        4. Response structure and status codes
        5. Authentication requirements
        
        SRS Document:
        {srs_document}
        
        Provide your analysis in a structured JSON format with a list of endpoints.
        """
    )
    
    # Prompt for database schema
    db_prompt = PromptTemplate.from_template(
        """
        You are a database architect specializing in schema design.
        
        Analyze the following Software Requirements Specification (SRS) document and extract the database schema that needs to be implemented.
        
        For each table/model, identify:
        1. The table name
        2. All fields/columns with their data types
        3. Primary keys and foreign keys
        4. Relationships with other tables
        5. Any constraints or validations
        
        SRS Document:
        {srs_document}
        
        Provide your analysis in a structured JSON format with a list of tables.
        """
    )
    
    logic_prompt = PromptTemplate.from_template(
        """
        You are a business analyst specializing in software requirements.
        
        Analyze the following Software Requirements Specification (SRS) document and extract the business logic that needs to be implemented.
        
        Identify:
        1. Core business rules
        2. Validation requirements
        3. Calculation or processing logic
        4. Workflow steps
        5. Integration requirements
        
        SRS Document:
        {srs_document}
        
        Provide your analysis in a structured JSON format with a list of business logic components.
        """
    )
    
    auth_prompt = PromptTemplate.from_template(
        """
        You are a security analyst specializing in authentication and authorization.
        
        Analyze the following Software Requirements Specification (SRS) document and extract the authentication and authorization requirements.
        
        Identify:
        1. Authentication methods (JWT, OAuth, etc.)
        2. User roles and permissions
        3. Access control requirements
        4. Security constraints
        
        SRS Document:
        {srs_document}
        
        Provide your analysis in a structured JSON format.
        """
    )
    
    try:

        import re
        def extract_json_from_llm_output(x):
            content = x.content.strip()
            match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if not match:
                raise ValueError("No JSON block found in LLM output")
            json_str = match.group(1)
            return json.loads(json_str)


        api_chain = api_prompt | llm | RunnableLambda(extract_json_from_llm_output)
        api_endpoints = api_chain.invoke({"srs_document": state.srs_document})
        state.api_endpoints = api_endpoints

        db_chain = db_chain = db_prompt | llm | RunnableLambda(extract_json_from_llm_output)
        database_schema = db_chain.invoke({"srs_document": state.srs_document})

        state.database_schema = database_schema
        
        logic_chain = logic_prompt | llm | RunnableLambda(extract_json_from_llm_output)
        business_logic = logic_chain.invoke({"srs_document": state.srs_document})
        state.business_logic = business_logic

        auth_chain = auth_prompt | llm | RunnableLambda(extract_json_from_llm_output)
        auth_requirements = auth_chain.invoke({"srs_document": state.srs_document})
        state.auth_requirements = auth_requirements
        
        # Add message to state
        state.messages.append({
                "role": "system",
                "content": "Successfully analyzed SRS document and extracted requirements"
            })
        
    except Exception as e:
        state.messages.append({
                "role": "system",
                "content": f"Error analyzing requirements: {str(e)}"
            })
        state.status = "failed"
    
    return state


def generate_project_structure(state: GraphState) -> GraphState:
    project_id = str(uuid.uuid4())
    state.project_id = project_id

    project_dir = Path("generated_projects") / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    state.project_path = str(project_dir)
    
    (project_dir / "app").mkdir(exist_ok=True)
    (project_dir / "app" / "api").mkdir(exist_ok=True)
    (project_dir / "app" / "api" / "routes").mkdir(exist_ok=True)
    (project_dir / "app" / "models").mkdir(exist_ok=True)
    (project_dir / "app" / "services").mkdir(exist_ok=True)
    (project_dir / "tests").mkdir(exist_ok=True)
    

    (project_dir / "app" / "__init__.py").touch()
    (project_dir / "app" / "api" / "__init__.py").touch()
    (project_dir / "app" / "api" / "routes" / "__init__.py").touch()
    (project_dir / "app" / "models" / "__init__.py").touch()
    (project_dir / "app" / "services" / "__init__.py").touch()
    
    state.generated_files.append({
        "path": str(project_dir),
        "type": "directory",
        "description": "Project root directory"
    })
    
    state.messages.append({
                "role": "system",
                "content": f"Generated project structure at {project_dir}"
            })
    return state

def generate_database_models(state: GraphState) -> GraphState:
    if not state.database_schema:
        state.messages.append({
                "role": "system",
                "content": "Error: No database schema to generate models from"
            })
        return state
    
    llm = get_llm()
    
    model_prompt = PromptTemplate.from_template(
        """
        You are a Python developer specializing in SQLAlchemy ORM.
        
        Generate SQLAlchemy models for the following database schema:
        
        {database_schema}
        
        Requirements:
        1. Use SQLAlchemy 2.0 syntax with type annotations
        2. Inherit from the Base class imported from app.services.database
        3. Include proper relationships between models
        4. Add appropriate indexes and constraints
        5. Include docstrings for each model and field
        
        For each model, create a separate file in the app/models directory.
        Provide the complete code for each model file.
        """
    )
    
    try:
        model_chain = model_prompt | llm
        model_response = model_chain.invoke({"database_schema": json.dumps(state.database_schema, indent=2)})
        model_files = []
        
        project_dir = Path(state.project_path)
        
        base_model_path = project_dir / "app" / "models" / "base.py"
        with open(base_model_path, "w") as f:
            f.write('''
            from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
            from sqlalchemy.orm import relationship
            from datetime import datetime
            from app.services.database import Base

            class TimestampMixin:
                """Mixin for adding timestamp fields to models"""
                created_at = Column(DateTime, default=datetime.utcnow)
                updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            ''')
        
        model_files.append({
            "path": str(base_model_path),
            "type": "file",
            "description": "Base model with timestamp mixin"
        })

        model_response_str = model_response.content if isinstance(model_response.content, str) else str(model_response.content)

        matches = re.findall(r"\*\*app/models/(.+?)\.py\*\*\n```python\n(.*?)```", model_response_str, re.DOTALL)
        for filename, code in matches:
            model_path = project_dir / "app" / "models" / f"{filename}.py"
            with open(model_path, "w") as f:
                f.write(code.strip())

            model_files.append({
                "path": str(model_path),
                "type": "file",
                "description": f"{filename}.py SQLAlchemy model"
            })

        state.generated_files.extend(model_files)
        
        state.messages.append({
                "role": "system",
                "content": f"Generated database models based on the extracted schema"
            })
        
    except Exception as e:
        state.messages.append({
                "role": "system",
                "content": f"Error generating database models: {str(e)}"
            })
    
    return state


def generate_main_application(state: GraphState) -> GraphState:
    """
    Generate the main FastAPI application file
    """
    project_dir = Path(state.project_path)
    
    try:
        main_path = project_dir / "app" / "main.py"
        with open(main_path, "w") as f:
            f.write("""
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="FastAPI Application",
    description="Generated FastAPI application",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
# from app.api.routes import your_router

# Register routers
# app.include_router(your_router.router, prefix="/api", tags=["Your Tag"])

# Startup event
@app.on_event("startup")
async def startup_event():
    # Initialize database connection
    from app.services.database import init_db
    await init_db()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    # Close database connection
    from app.services.database import close_db
    await close_db()

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the FastAPI Application",
        "docs": "/docs",
        "version": app.version,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
""")
        
        db_path = project_dir / "app" / "services" / "database.py"
        with open(db_path, "w") as f:
            f.write('''
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/fastapi_db")

# Convert standard PostgreSQL URL to async format
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",
    future=True,
    poolclass=NullPool,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
async def get_db():
    """
    Dependency function that yields a SQLAlchemy async session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Context manager for database session
@asynccontextmanager
async def db_session():
    """
    Context manager for database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database
async def init_db():
    """
    Initialize database connection
    """
    # In a production environment, you might want to use Alembic for migrations
    # This is a simple initialization for development
    async with engine.begin() as conn:
        # Uncomment the following line to create tables on startup (development only)
        # await conn.run_sync(Base.metadata.create_all)
        pass

# Close database connection
async def close_db():
    """
    Close database connection
    """
    await engine.dispose()
''')
        
        # Add to generated files
        state.generated_files.append({
            "path": str(main_path),
            "type": "file",
            "description": "Main FastAPI application"
        })
        
        state.generated_files.append({
            "path": str(db_path),
            "type": "file",
            "description": "Database service"
        })
        
        state.messages.append({
                "role": "system",
                "content":  f"Generated main FastAPI application file"
            })
        
    except Exception as e:
        state.messages.append({
                "role": "system",
                "content": f"Error generating main application: {str(e)}"
            })
    
    return state

def generate_api_routes(state: GraphState) -> GraphState:
    """
    Generate API routes based on the extracted endpoints
    """
    if not state.api_endpoints:
        state.messages.append({
                "role": "system",
                "content": "Error: No API endpoints to generate routes from"
            })
        return state
    
    llm = get_llm()
    
    route_prompt = PromptTemplate.from_template(
        """
        You are a Python developer specializing in FastAPI.
        
        Generate FastAPI route files for the following API endpoints:
        
        {api_endpoints}
        
        Database Schema:
        {database_schema}
        
        Business Logic:
        {business_logic}
        
        Authentication Requirements:
        {auth_requirements}
        
        Requirements:
        1. Use FastAPI's dependency injection for database sessions
        2. Implement proper request and response models using Pydantic
        3. Include appropriate error handling
        4. Add comprehensive docstrings and OpenAPI documentation
        5. Implement authentication and authorization as required
        
        For each logical group of endpoints, create a separate file in the app/api/routes directory.
        Provide the complete code for each route file.
        """
    )
    
    try:
        route_chain = route_prompt | llm
        route_response = route_chain.invoke({
            "api_endpoints": json.dumps(state.api_endpoints, indent=2),
            "database_schema": json.dumps(state.database_schema, indent=2),
            "business_logic": json.dumps(state.business_logic, indent=2),
            "auth_requirements": json.dumps(state.auth_requirements, indent=2)
        })

        route_files = []

        content = route_response.content
        code_blocks = re.findall(r"\*\*(.*?)\*\*\s*```python(.*?)```", content, re.DOTALL)

        for filename, code in code_blocks:  
            filename = filename.strip()
            file_path = Path(state.project_path) / "app" / "api" / "routes" / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w") as f:
                f.write(code.strip())

            route_files.append(str(file_path.relative_to(state.project_path)))

        state.generated_files.extend(route_files)
        project_dir = Path(state.project_path)
        state.generated_files.extend(route_files)
        
        state.messages.append({
                "role": "system",
                "content": f"Generated API routes based on the extracted endpoints"
            })
        
    except Exception as e:
        state.messages.append({
                "role": "system",
                "content": f"Error generating API routes: {str(e)}"
            })
    
    return state


def generate_config_files(state: GraphState) -> GraphState:
    """
    Generate configuration files for the FastAPI application
    """
    project_dir = Path(state.project_path)
    config_files = []
    
    try:
        requirements_path = project_dir / "requirements.txt"
        with open(requirements_path, "w") as f:
            f.write("""
# FastAPI and ASGI server
fastapi>=0.104.0
uvicorn>=0.23.2
python-multipart>=0.0.6

# Database
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.9
asyncpg>=0.28.0

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Testing
pytest>=7.4.2
httpx>=0.25.0

# Utilities
pydantic>=2.4.2
python-dotenv>=1.0.0
email-validator>=2.0.0
""")
        
        config_files.append({
            "path": str(requirements_path),
            "type": "file",
            "description": "Project dependencies"
        })

        env_example_path = project_dir / ".env.example"
        with open(env_example_path, "w") as f:
            f.write("""
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/fastapi_db

# JWT Configuration
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
APP_ENV=development
DEBUG=True
""")
        
        config_files.append({
            "path": str(env_example_path),
            "type": "file",
            "description": "Environment variables example"
        })

        dockerfile_path = project_dir / "Dockerfile"
        with open(dockerfile_path, "w") as f:
            f.write("""
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")
        
        config_files.append({
            "path": str(dockerfile_path),
            "type": "file",
            "description": "Docker configuration"
        })
        
        docker_compose_path = project_dir / "docker-compose.yml"
        with open(docker_compose_path, "w") as f:
            f.write("""
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/fastapi_db
      - SECRET_KEY=your_secret_key
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      - APP_ENV=development
      - DEBUG=True
    volumes:
      - .:/app
    restart: always

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fastapi_db
    ports:
      - "5432:5432"

volumes:
  postgres_data:
""")
        
        config_files.append({
            "path": str(docker_compose_path),
            "type": "file",
            "description": "Docker Compose configuration"
        })
        
        readme_path = project_dir / "README.md"
        with open(readme_path, "w") as f:
            f.write(f"""
# FastAPI Project

This FastAPI project was automatically generated based on an SRS document using LangGraph.

## Project Structure

```
project_root/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   └── ...
│   │   └── __init__.py
│   ├── models/
│   │   └── ...
│   ├── services/
│   │   └── ...
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── ...
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\\Scripts\\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and update the values
6. Run the application: `uvicorn app.main:app --reload`

## Docker Setup

1. Build and start the containers: `docker-compose up -d`
2. The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest: `pytest`
""")
        
        config_files.append({
            "path": str(readme_path),
            "type": "file",
            "description": "Project documentation"
        })
        
        state.generated_files.extend(config_files)
        
        state.messages.append({
                "role": "system",
                "content": f"Generated configuration files for the FastAPI application"
            })
        
    except Exception as e:
        state.messages.append({
                "role": "system",
                "content": f"Error generating configuration files: {str(e)}"
            })
    
    return state


def generate_documentation(state: GraphState) -> GraphState:
    """
    Generate documentation for the FastAPI application
    """
    project_dir = Path(state.project_path)
    
    try:
        api_docs_path = project_dir / "docs" / "api.md"
        api_docs_path.parent.mkdir(exist_ok=True)
        
        with open(api_docs_path, "w") as f:
            f.write(f"""
# API Documentation

## Endpoints

{json.dumps(state.api_endpoints, indent=2)}

## Authentication

{json.dumps(state.auth_requirements, indent=2)}

## Database Schema

{json.dumps(state.database_schema, indent=2)}

## Business Logic

{json.dumps(state.business_logic, indent=2)}
""")
        
        workflow_docs_path = project_dir / "docs" / "workflow.md"
        with open(workflow_docs_path, "w") as f:
            f.write("""
# LangGraph Workflow

```mermaid
graph TD
    A[Parse SRS Document] --> B[Analyze Requirements]
    B --> C[Generate Project Structure]
    C --> D[Generate Database Models]
    D --> E[Generate API Routes]
    E --> F[Generate Tests]
    F --> G[Generate Configuration Files]
    G --> H[Generate Main Application]
    H --> I[Generate Documentation]
```

## Workflow Nodes

1. **Parse SRS Document**: Extract text content from the SRS document
2. **Analyze Requirements**: Extract API endpoints, database schema, business logic, and authentication requirements
3. **Generate Project Structure**: Create the basic project directory structure
4. **Generate Database Models**: Create SQLAlchemy models based on the database schema
5. **Generate API Routes**: Create FastAPI routes based on the API endpoints
6. **Generate Tests**: Create pytest tests
7. **Generate Configuration Files**: Create configuration files like requirements.txt, Dockerfile, etc.
8. **Generate Main Application**: Create the main FastAPI application file
9. **Generate Documentation**: Create documentation for the API and workflow
""")
        
        state.generated_files.append({
            "path": str(api_docs_path),
            "type": "file",
            "description": "API documentation"
        })
        
        state.generated_files.append({
            "path": str(workflow_docs_path),
            "type": "file",
            "description": "LangGraph workflow documentation"
        })
        
        state.messages.append({
                "role": "system",
                "content": f"Generated documentation for the FastAPI application"
            })
    except Exception as e:
        state.messages.append({
                "role": "system",
                "content": f"Error generating documentation: {str(e)}"
            })
    return state


def validate_output(state: GraphState) -> GraphState:
    """
    Validate the generated output and determine if regeneration is needed
    """
    llm = get_llm(temperature=0.1)  # Lower temperature for more consistent validation
    
    # Prompt for validation
    validation_prompt = PromptTemplate.from_template(
        """
        You are a quality assurance expert specializing in FastAPI applications.
        
        Evaluate the following generated FastAPI project based on the requirements:
        
        API Endpoints:
        {api_endpoints}
        
        Database Schema:
        {database_schema}
        
        Business Logic:
        {business_logic}
        
        Authentication Requirements:
        {auth_requirements}
        
        Generated Files:
        {generated_files}
        
        Evaluate the following aspects:
        1. Completeness: Does the project include all required components?
        2. Correctness: Are the implementations correct and follow best practices?
        3. Consistency: Are naming conventions and patterns consistent?
        4. Functionality: Would the application work as expected?
        5. Security: Are security best practices followed?
        
        Provide your evaluation in a structured JSON format with the following fields:
        - "valid": boolean indicating if the project is valid
        - "score": integer from 0-100 indicating overall quality
        - "issues": list of identified issues
        - "recommendations": list of recommendations for improvement
        - "regeneration_needed": boolean indicating if regeneration is needed
        - "regeneration_target": string indicating which component needs regeneration (if applicable)
          Valid regeneration targets are: "generate_database_models", "generate_api_routes", "generate_tests", 
          "generate_config_files", "generate_main_application", "generate_documentation"
        """
    )
    
    try:
        # Validate output
        validation_chain = validation_prompt | llm | RunnableLambda(
            lambda x: json.loads(re.search(r'```json\n(.*?)\n```', x.content, re.DOTALL).group(1))
        )

        validation_results = validation_chain.invoke({
            "api_endpoints": json.dumps(state.api_endpoints, indent=2),
            "database_schema": json.dumps(state.database_schema, indent=2),
            "business_logic": json.dumps(state.business_logic, indent=2),
            "auth_requirements": json.dumps(state.auth_requirements, indent=2),
            "generated_files": json.dumps(state.generated_files, indent=2)
        })
        
        state.validation_results = validation_results
        
        if validation_results.get("regeneration_needed", False):
            state.regeneration_count += 1
            
            regeneration_target = validation_results.get("regeneration_target")
            
            valid_targets = [
                "generate_database_models", 
                "generate_api_routes", 
                "generate_tests", 
                "generate_config_files", 
                "generate_main_application", 
                "generate_documentation"
            ]
            
            if regeneration_target in valid_targets:
                state.regeneration_target = regeneration_target
            else:
                state.regeneration_target = "generate_api_routes"
                state.messages.append({
                "role": "system",
                "content": f"Invalid regeneration target '{regeneration_target}'. Defaulting to 'generate_api_routes'."
                })
            
            state.messages.append({
                "role": "system",
                "content": f"Validation failed. Regenerating {state.regeneration_target}. Attempt {state.regeneration_count} of {state.max_regenerations}."
                })
            
            if state.regeneration_count >= state.max_regenerations:
                state.messages.append({
                "role": "system",
                "content": f"Maximum regeneration attempts reached. Proceeding with current output."
                })
                state.regeneration_target = None
        else:
            state.messages.append({
                "role": "system",
                "content": f"Validation successful. Project generated successfully."
                })

            state.regeneration_target = None
        
    except Exception as e:
        print(e)
        state.messages.append({
                "role": "system",
                "content": f"Error validating output: {str(e)}"
                })
        
        state.regeneration_target = None
    
    return state


def create_workflow() -> StateGraph:

    workflow = StateGraph(GraphState)
    
    workflow.add_node("parse_srs_document", parse_srs_document)
    workflow.add_node("analyze_requirements", analyze_requirements)
    workflow.add_node("generate_project_structure", generate_project_structure)
    workflow.add_node("generate_database_models", generate_database_models)
    workflow.add_node("generate_api_routes", generate_api_routes)
    workflow.add_node("generate_config_files", generate_config_files)
    workflow.add_node("generate_main_application", generate_main_application)
    workflow.add_node("generate_documentation", generate_documentation)
    workflow.add_node("validate_output", validate_output)

    workflow.add_edge(START, "parse_srs_document")
    workflow.add_edge("parse_srs_document", "analyze_requirements")
    workflow.add_edge("analyze_requirements", "generate_project_structure")
    workflow.add_edge("generate_project_structure", "generate_database_models")
    workflow.add_edge("generate_database_models", "generate_api_routes")
    workflow.add_edge("generate_api_routes", "generate_config_files")
    workflow.add_edge("generate_config_files", "generate_main_application")
    workflow.add_edge("generate_main_application", "generate_documentation")
    workflow.add_edge("generate_documentation", "validate_output")
    
    workflow.add_conditional_edges(
        "validate_output",
        lambda state: END if state.regeneration_target is None else state.regeneration_target
    )
    return workflow.compile()
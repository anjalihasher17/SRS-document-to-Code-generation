
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

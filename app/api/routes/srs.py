import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from services.database import get_db
# Import the process_srs_document function
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from workflow.workflow import process_srs_document


router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


GENERATED_DIR = Path("generated_projects")
GENERATED_DIR.mkdir(exist_ok=True)

# Response models
class SRSProcessingResponse(BaseModel):
    """Response model for SRS processing"""
    job_id: str
    message: str
    status: str

class ProjectGenerationResponse(BaseModel):
    """Response model for project generation"""
    project_id: str
    project_path: str
    langsmith_trace_url: Optional[str] = None
    message: str

@router.post("/srs/upload", response_model=SRSProcessingResponse)
async def upload_srs_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an SRS document for processing
    
    - Accepts only .docx files
    - Validates file format and content
    - Returns a job ID for tracking the processing
    """
    # Validate file format
    if not file.filename.endswith(".docx"):
        raise HTTPException(
            status_code=400, 
            detail="Only .docx files are supported"
        )
    
    # Generate unique ID for this job
    job_id = str(uuid.uuid4())
    
    # Create directory for this job
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    # Save uploaded file
    file_path = job_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process the document in the background
    background_tasks.add_task(
        process_srs_document_task,
        file_path=str(file_path),
        job_id=job_id
    )
    
    return SRSProcessingResponse(
        job_id=job_id,
        message=f"SRS document '{file.filename}' uploaded successfully. Processing started.",
        status="processing"
    )

# Endpoint to get processing status
@router.get("/srs/status/{job_id}", response_model=SRSProcessingResponse)
async def get_processing_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of an SRS document processing job
    
    - Returns the current status of the processing
    - If completed, returns the project generation details
    """
    # Check if job exists
    job_dir = UPLOAD_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Job with ID {job_id} not found"
        )
    
    # Check if processing is complete
    status_file = job_dir / "status.txt"
    if status_file.exists():
        status = status_file.read_text().strip()
        
        if status == "completed":
            # Get project details
            project_id_file = job_dir / "project_id.txt"
            if project_id_file.exists():
                project_id = project_id_file.read_text().strip()
                return SRSProcessingResponse(
                    job_id=job_id,
                    message=f"Processing completed. Project ID: {project_id}",
                    status="completed"
                )
        elif status == "failed":
            error_file = job_dir / "error.txt"
            error_message = "Processing failed"
            if error_file.exists():
                error_message = error_file.read_text().strip()
            
            return SRSProcessingResponse(
                job_id=job_id,
                message=error_message,
                status="failed"
            )
    
    # If no status file or status is not completed/failed
    return SRSProcessingResponse(
        job_id=job_id,
        message="Processing in progress",
        status="processing"
    )

# Endpoint to get generated project
@router.get("/srs/project/{project_id}", response_model=ProjectGenerationResponse)
async def get_generated_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a generated project
    
    - Returns the project path and LangSmith trace URL
    """
    # Check if project exists
    project_dir = GENERATED_DIR / project_id
    if not project_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Project with ID {project_id} not found"
        )
    
    # Get LangSmith trace URL if available
    langsmith_file = project_dir / "langsmith_trace.txt"
    langsmith_trace_url = None
    if langsmith_file.exists():
        langsmith_trace_url = langsmith_file.read_text().strip()
    
    return ProjectGenerationResponse(
        project_id=project_id,
        project_path=str(project_dir),
        langsmith_trace_url=langsmith_trace_url,
        message="Project generated successfully"
    )

def zip_generated_project(output_dir: str, zip_file_name: str = "generated_project.zip") -> str:
    zip_path = os.path.join(os.path.dirname(output_dir), zip_file_name)
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', output_dir)
    return zip_path

async def process_srs_document_task(file_path: str, job_id: str):
    """
    Background task to process an SRS document
    
    - Analyzes the document using LangGraph
    - Generates a FastAPI project
    - Updates the job status
    """
    job_dir = UPLOAD_DIR / job_id
    status_file = job_dir / "status.txt"
    
    try:
        with open(status_file, "w") as f:
            f.write("processing")
        
        project_id, langsmith_trace_url = await process_srs_document(file_path)

        with open(job_dir / "project_id.txt", "w") as f:
            f.write(project_id)
        
        if langsmith_trace_url:
            with open(GENERATED_DIR / project_id / "langsmith_trace.txt", "w") as f:
                f.write(langsmith_trace_url)
        
        with open(status_file, "w") as f:
            f.write("completed")

        generated_project_path = GENERATED_DIR / project_id

        zip_path = zip_generated_project(generated_project_path)

            
    except Exception as e:
        with open(job_dir / "error.txt", "w") as f:
            f.write(str(e))
        
        with open(status_file, "w") as f:
            f.write("failed")

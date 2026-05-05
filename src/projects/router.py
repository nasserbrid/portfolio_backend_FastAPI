from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.projects.dependencies import get_project_service
from src.projects.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from src.projects.service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectResponse])
async def get_all(service: ProjectService = Depends(get_project_service)):
    return await service.get_all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_by_id(project_id: int, service: ProjectService = Depends(get_project_service)):
    return await service.get_by_id(project_id)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create(
    title: str = Form(...),
    description: str = Form(...),
    skills: str = Form(...),
    image_url: str | None = Form(None),
    image: UploadFile | None = File(None),
    service: ProjectService = Depends(get_project_service),
):
    data = ProjectCreate(title=title, description=description, skills=skills, image_url=image_url)
    return await service.create(data, image)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update(
    project_id: int,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    return await service.update(project_id, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(project_id: int, service: ProjectService = Depends(get_project_service)):
    await service.delete(project_id)

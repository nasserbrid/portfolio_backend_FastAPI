from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
    title: str
    description: str
    skills: str


class ProjectCreate(ProjectBase):
    image_url: str | None = None


class ProjectUpdate(ProjectBase):
    image_url: str | None = None


class ProjectResponse(ProjectBase):
    id: int
    image_url: str

    model_config = ConfigDict(from_attributes=True)

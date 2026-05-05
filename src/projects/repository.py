from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.projects.models import Project


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Project]:
        result = await self.db.execute(select(Project))
        return list(result.scalars().all())

    async def get_by_id(self, project_id: int) -> Project | None:
        return await self.db.get(Project, project_id)

    async def create(self, project: Project) -> Project:
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update(self, project: Project) -> Project:
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.db.delete(project)
        await self.db.commit()

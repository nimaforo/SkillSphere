# projects/ports/repositories.py
from abc import ABC, abstractmethod
from projects.domain.entities import ProjectEntity

class ProjectRepositoryPort(ABC):
    
    @abstractmethod
    def create(self, project_entity: ProjectEntity, tags_names: list) -> ProjectEntity:
        pass

    @abstractmethod
    def get_all(self) -> list[ProjectEntity]:
        pass
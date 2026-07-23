from abc import ABC, abstractmethod
from users.domain.entities import UserEntity

class UserRepositoryPort(ABC):
    
    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity:
        pass

    @abstractmethod
    def create(self, user_entity: UserEntity, password: str) -> UserEntity:
        pass
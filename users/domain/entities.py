# users/domain/entities.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class UserEntity:
    id: Optional[int]
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False
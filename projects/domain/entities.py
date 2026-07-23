# projects/domain/entities.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class TagEntity:
    id: Optional[int]
    name: str

@dataclass
class ProjectEntity:
    id: Optional[int]
    title: str
    description: str
    file_url: str
    file_size: int  # به بایت
    user_id: int    # شناسه کاربری که پروژه را آپلود کرده
    created_at: datetime
    tags: List[TagEntity] = field(default_factory=list)

    def is_large_file(self, max_size_mb: int = 50) -> bool:
        """بررسی اینکه آیا حجم فایل از حد مجاز بیشتر است یا خیر"""
        return self.file_size > (max_size_mb * 1024 * 1024)
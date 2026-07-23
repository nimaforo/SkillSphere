# projects/adapters/db_repository.py
from projects.models import Project
from projects.domain.entities import ProjectEntity

class DjangoProjectRepositoryAdapter:
    def get_all(self):
        # دریافت تمام پروژه‌ها از دیتابیس جنگو
        django_projects = Project.objects.all().prefetch_related('likes')
        project_entities = []
        
        for p in django_projects:
            project_entities.append(
                ProjectEntity(
                    id=p.id,
                    title=p.title,
                    description=p.description,
                    file_url=p.file.url if p.file else '',
                    file_size=p.file.size if p.file else 0,
                    user_id=p.user_id,
                    created_at=p.created_at,
                    tags=[]
                )
            )
        return project_entities

    def create(self, project_entity: ProjectEntity, uploaded_file) -> ProjectEntity:
        # ۱. ذخیره پروژه در مدل جنگو
        django_project = Project.objects.create(
            title=project_entity.title,
            description=project_entity.description,
            file=uploaded_file,
            user_id=project_entity.user_id
        )
            
        # ۲. به روز رسانی انتیتی با ID تولید شده دیتابیس
        project_entity.id = django_project.id
        project_entity.file_url = django_project.file.url
        
        return django_project
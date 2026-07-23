from users.ports.repositories import UserRepositoryPort
from users.domain.entities import UserEntity
from users.models import UserModel

class DjangoUserRepositoryAdapter(UserRepositoryPort):
    
    def _to_entity(self, django_user: UserModel) -> UserEntity:
        """تبدیل مدل جنگو به انتتی دامین"""
        return UserEntity(
            id=django_user.id,
            username=django_user.username,
            email=django_user.email,
            is_active=django_user.is_active,
            created_at=django_user.date_joined
        )

    def get_by_email(self, email: str) -> UserEntity:
        try:
            django_user = UserModel.objects.get(email=email)
            return self._to_entity(django_user)
        except UserModel.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> UserEntity:
        try:
            django_user = UserModel.objects.get(username=username)
            return self._to_entity(django_user)
        except UserModel.DoesNotExist:
            return None

    def create(self, user_entity: UserEntity, password: str) -> UserEntity:
        # ساخت کاربر در دیتابیس جنگو همراه با هش کردن پسورد
        django_user = UserModel.objects.create_user(
            username=user_entity.username,
            email=user_entity.email,
            password=password
        )
        return self._to_entity(django_user)
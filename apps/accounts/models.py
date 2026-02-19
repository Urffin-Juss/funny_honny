from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    PACKER = "packer", "Packer"


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.PACKER)

    @property
    def is_manager(self) -> bool:
        return self.role in {UserRole.OWNER, UserRole.ADMIN}

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    """
    Custom User Manager to handle user creation and superuser creation.
    Automatically assigns roles:
        - 'advisor' for superusers
        - 'client' for all other users
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'client')  # Default role is client
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'advisor')  # Superusers are advisors
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('advisor', 'Conseiller Bancaire'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)  # Email as unique identifier

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Keep username for compatibility

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Assign role based on superuser status
        if self.is_superuser:
            self.role = 'advisor'
        elif not self.role:
            self.role = 'client'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"
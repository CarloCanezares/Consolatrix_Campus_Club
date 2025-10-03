from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # Set username to email if not provided
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    # Override the groups field with a custom related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='ccc_users',
        related_query_name='ccc_user',
        help_text='The groups this user belongs to.'
    )
    
    # Override the user_permissions field with a custom related_name
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='ccc_users_permissions',
        related_query_name='ccc_user_permission',
        help_text='Specific permissions for this user.'
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    student_id = models.CharField(max_length=10, unique=True)
    year_level = models.IntegerField(null=True)
    phone = models.CharField(max_length=15)
    bio = models.TextField(blank=True)
    interests = models.JSONField(default=list)
    newsletter = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
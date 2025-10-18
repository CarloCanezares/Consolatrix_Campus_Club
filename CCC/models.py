from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.utils import timezone

# Update your CustomUserManager in models.py

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
        
        # Generate a student_id for superuser if not provided
        if 'student_id' not in extra_fields or not extra_fields['student_id']:
            import uuid
            extra_fields['student_id'] = f"ADMIN-{uuid.uuid4().hex[:6].upper()}"
        
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

    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Student's department/college"
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
    student_id = models.CharField(max_length=20, unique=True)  # Changed from 10 to 20
    year_level = models.IntegerField(null=True)
    phone = models.CharField(max_length=15, blank=True, default='')
    bio = models.TextField(blank=True)
    interests = models.JSONField(default=list)
    newsletter = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Club(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='clubs',
        blank=True,
        help_text='Users who are accepted members of this club'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()
    member_count.short_description = 'Members'


class ClubApplication(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='club_applications'
    )
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_applications'
    )

    class Meta:
        unique_together = ('user', 'club')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} → {self.club.name} ({self.status})"
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager,Permission, Group
import uuid
from django.utils import timezone
import json

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    first_name = models.CharField(max_length=15,blank=True, null=True)
    last_name = models.CharField(max_length=35, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11,blank=True)
    address = models.CharField(max_length=50, )
    password = models.CharField(max_length=128, blank=True, null=True) 
    password2 = models.CharField(max_length=128, blank=True, null=True) 
    preferred_language = models.CharField(max_length=30, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    ROLE = (
        ('client', "Client"),
        ('vendor', "Vendor"),
        ('admin', "Admin"),
    )
    
    STATUS = (
        ('D', 'deleted'),
        ('I', 'inactive'),
        ('A', 'active'),
        ('U', 'unverified'),
    )
    role = models.CharField(max_length=20, choices=ROLE, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, null=True,blank= True)
    SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    
    objects = UserManager()
    
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True
    )
    
    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = ['phone']
    
    location = models.CharField(max_length=100, blank=True, null=True)
    
    
    education = models.CharField(max_length=100, blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, null=True)
    job = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, default='United States')
    
    # For JSON fields
    _social = models.TextField(blank=True, default='{}')
    _notifications = models.TextField(blank=True, default='{}')
    
    @property
    def social(self):
        try:
            return json.loads(self._social)
        except json.JSONDecodeError:
            return {}
    
    @social.setter
    def social(self, value):
        self._social = json.dumps(value if value else {})
    
    @property
    def notifications(self):
        try:
            return json.loads(self._notifications)
        except json.JSONDecodeError:
            return {}
    
    @notifications.setter
    def notifications(self, value):
        self._notifications = json.dumps(value if value else {})
    class Meta:
        db_table = 'accounts_user'
        
    def __str__(self):
        return self.email
    def save(self, *args, **kwargs):
    # Generate username if not exists (your existing functionality)
        if not self.username:
            self.username = str(uuid.uuid4())[:30]
        
        # Security check for admin registration (new functionality)
        if not self.pk:  # Only for new users
            if self.role == 'admin' and not (self.is_staff or self.is_superuser):
                # This is a public registration attempt to create admin
                self.role = 'client'  # Downgrade to client role
                self.is_staff = False
                self.is_superuser = False
        
        # For existing users being promoted to admin
        elif self.role == 'admin' and not (self.is_staff and self.is_superuser):
            # Only allow role change to admin if already staff+superuser
            self.role = User.objects.get(pk=self.pk).role  # Revert role change
        
        super().save(*args, **kwargs)
        
   
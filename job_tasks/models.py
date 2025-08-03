from django.db import models
from accounts.models import User
# Create your models here.
class Job(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    job_id = models.CharField(max_length=20, unique=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_jobs')
    welder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='welder_jobs')
    job_type = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class Task(models.Model):
    PRIORITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField()
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    completed = models.BooleanField(default=False)

class Material(models.Model):
    STATUS_CHOICES = (
        ('in_stock', 'In Stock'),
        ('low', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    )
    name = models.CharField(max_length=100)
    material_type = models.CharField(max_length=50)
    quantity = models.IntegerField()
    location = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    threshold = models.IntegerField()
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True)
    experience = models.TextField()
    education = models.TextField()
    skills = models.TextField()
    source = models.CharField(max_length=50, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
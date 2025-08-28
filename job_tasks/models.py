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
    title = models.CharField(max_length=50,default='')
    job_id = models.CharField(max_length=20, unique=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_jobs')
    welder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='welder_jobs')
    job_type = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
    
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
    
    class Meta:
        db_table = 'tasks'
        ordering = ['due_date']

class Material(models.Model):
    STATUS_CHOICES = (
        ('in_stock', 'In Stock'),
        ('low', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    )
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    material_type = models.CharField(max_length=50)
    quantity = models.IntegerField()
    location = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    threshold = models.IntegerField()
    
    class Meta:
        db_table = 'materials'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

class Application(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='resumes/%Y/%m/%d/')
    cover_letter = models.TextField(blank=True)
    experience = models.TextField()
    education = models.TextField()
    skills = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    source = models.CharField(max_length=50, default='website')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'applications'
        ordering = ['-submitted_at']

    class Meta:
        db_table = 'job_applications'
        unique_together = ['job', 'user'] 
        
class ReportIssue(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='issues')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_issues')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reported_issues'
        ordering = ['-created_at']

    def __str__(self):
        return f"Issue '{self.title}' reported by {self.reported_by.username} for {self.job.title}"

class LogWork(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='work_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_logs')
    date = models.DateField(auto_created=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'work_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Work log for {self.job.title} by {self.user.username} on {self.date}"
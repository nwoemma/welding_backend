from rest_framework import serializers
from accounts.models import User 
from job_tasks.models import Job,Task, Material, Notification, Application, ReportIssue,LogWork
from django.utils.timesince import timesince
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Includes all fields
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)
class ProfileSerializer(serializers.ModelSerializer):
    profile_pic_url = serializers.SerializerMethodField()
    social = serializers.JSONField(required=False)
    notifications = serializers.JSONField(required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 
            'address', 'role', 'profile_pic', 'profile_pic_url',
            'education', 'skills', 'job', 'company', 'about',
            'country', 'social', 'notifications'
        ]
        extra_kwargs = {
            'profile_pic': {'write_only': True},
            'email': {'read_only': True}
        }
    
    def get_profile_pic_url(self, obj):
        if obj.profile_pic:
            return self.context['request'].build_absolute_uri(obj.profile_pic.url)
        return None
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure social and notifications are always objects
        data['social'] = instance.social if hasattr(instance, 'social') else {}
        data['notifications'] = instance.notifications if hasattr(instance, 'notifications') else {}
        return data

class JobSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    welder_name = serializers.CharField(source='welder.get_full_name', read_only=True)
    
    class Meta:
        model = Job
        fields = '__all__'
        
class TaskSerializer(serializers.ModelSerializer):
    job_id = serializers.CharField(source='job.job_id', read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    
    def get_time(self, obj):
        return timesince(obj.created_at) + ' ago'
    
    class Meta:
        model = Notification
        fields = ['id', 'message', 'read', 'time']
        
class DashboardSerializer(serializers.Serializer):
    user = UserSerializer(read_only=True)
    jobs =  JobSerializer(read_only=True, many=True)
    notifications = NotificationSerializer(read_only=True, many=True)
    materials = MaterialSerializer(read_only=True, many=True)
    recent_jobs = JobSerializer(read_only=True, many=True)
    tasks = TaskSerializer(read_only=True, many=True)
    total_users = serializers.IntegerField()
    unread_notifications_count = serializers.IntegerField()
    total_jobs = serializers.IntegerField()
    materials_count = serializers.IntegerField()
    job_count = serializers.IntegerField()
    task_count = serializers.IntegerField()
    total_notifications = serializers.IntegerField()
    recent_users = UserSerializer(read_only=True, many=True)
    active_users = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    
    # def get_user(self, obj):
    #     user = obj['user']
    #     return {
    #         'first_name': user.first_name,
    #         'last_name': user.last_name,
    #         'role': user.role
    #     }

    # def get_stats(self, obj):
    #     return [
    #         {'label': 'Jobs', 'value': obj['job_count']},
    #         {'label': 'Materials', 'value': obj['material_count']},
    #         {'label': 'Tasks', 'value': obj['task_count']},
    #         {'label': 'Notifications', 'value': obj['notification_count']}
    #     ]

    # def get_notifications(self, obj):
    #     notifications = obj['notifications']
    #     return [{
    #         'id': n.id,
    #         'message': n.message,
    #         'read': n.read,
    #         'time': self.format_time(n.created_at)
    #     } for n in notifications]

    # def get_recent_jobs(self, obj):
    #     jobs = obj['jobs'][:5]  # Get first 5 jobs
    #     return [{
    #         'id': job.id,
    #         'job_id': job.job_number,
    #         'status': job.status,
    #         'deadline': job.deadline.strftime('%Y-%m-%d') if job.deadline else None
    #     } for job in jobs]

    # def get_upcoming_tasks(self, obj):
    #     tasks = obj['tasks']
    #     return [{
    #         'id': task.id,
    #         'description': task.description,
    #         'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
    #         'priority': task.priority
    #     } for task in tasks]

    # def get_unread_notifications(self, obj):
    #     return obj['notification_count']

    # def get_activity_chart(self, obj):
    #     if obj['user'].role != 'admin':
    #         return None
            
    #     # Example: Last 7 days job creation activity
    #     end_date = timezone.now()
    #     start_date = end_date - timedelta(days=7)
        
    #     return {
    #         'type': 'bar',
    #         'data': {
    #             'labels': [(start_date + timedelta(days=i)).strftime('%a') for i in range(7)],
    #             'datasets': [{
    #                 'label': 'Jobs Created',
    #                 'data': [10, 15, 7, 12, 9, 14, 8],  # Replace with actual data
    #                 'backgroundColor': 'rgba(75, 192, 192, 0.2)'
    #             }]
    #         }
    #     }

    # def get_project_timeline(self, obj):
    #     if obj['user'].role != 'client':
    #         return None
            
    #     return {
    #         'type': 'line',
    #         'data': {
    #             'labels': ['Design', 'Material Prep', 'Welding', 'Inspection', 'Delivery'],
    #             'datasets': [{
    #                 'label': 'Project Progress',
    #                 'data': [30, 50, 80, 90, 100],
    #                 'borderColor': 'rgba(54, 162, 235, 1)'
    #             }]
    #         }
    #     }

    # def get_productivity_chart(self, obj):
    #     if obj['user'].role != 'welder':
    #         return None
            
    #     return {
    #         'type': 'pie',
    #         'data': {
    #             'labels': ['Completed', 'In Progress', 'Pending'],
    #             'datasets': [{
    #                 'data': [15, 8, 3],
    #                 'backgroundColor': [
    #                     'rgba(75, 192, 192, 0.2)',
    #                     'rgba(255, 206, 86, 0.2)',
    #                     'rgba(255, 99, 132, 0.2)'
    #                 ]
    #             }]
    #         }
    #     }

    # def get_user_distribution(self, obj):
    #     return {
    #         'type': 'pie',
    #         'title': 'User Role Distribution',
    #         'data': {
    #             'labels': ['Admins', 'Managers', 'Users', 'Guests'],
    #             'datasets': [{
    #                 'label': 'User Count',
    #                 'data': [5, 12, 45, 8],
    #                 'backgroundColor': [
    #                     'rgba(255, 99, 132, 0.6)',
    #                     'rgba(54, 162, 235, 0.6)',
    #                     'rgba(255, 206, 86, 0.6)',
    #                     'rgba(75, 192, 192, 0.6)'
    #                 ],
    #             }]
    #         }
    #     }
    
    # def format_time(self, datetime):
    #     now = timezone.now()
    #     diff = now - datetime
        
    #     if diff.days > 0:
    #         return f"{diff.days}d ago"
    #     elif diff.seconds > 3600:
    #         return f"{diff.seconds // 3600}h ago"
    #     elif diff.seconds > 60:
    #         return f"{diff.seconds // 60}m ago"
    #     return "Just now"
    
class ApplicationSerializer(serializers.ModelSerializer):
    resume_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'status', 'first_name', 'last_name',
            'email', 'phone', 'resume_url', 'cover_letter',
            'experience', 'education', 'skills', 'source',
            'submitted_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'submitted_at', 'updated_at']
        
    def get_resume_url(self, obj):
        if obj.resume:
            return self.context['request'].build_absolute_uri(obj.resume.url)
        return None
        
class JobSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    welder = UserSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name='Client'),
        source='client',
        write_only=True
    )
    
    welder_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name='Welder'),
        source='welder',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Job
        fields = [
            'id', 'job_id', 'client', 'welder', 'client_id', 'welder_id',
            'job_type', 'description', 'status', 'deadline',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_job_id(self, value):
        # Check if job_id is unique when creating
        if self.instance is None and Job.objects.filter(job_id=value).exists():
            raise serializers.ValidationError("A job with this ID already exists.")
        return value

class ReportIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportIssue
        fields = ['id', 'title', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
        
class LogWorkSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = LogWork
        fields = ['id', 'user', 'job', 'hours_worked', 'date', 'created_at', 'updated_at', 'job_title', 'username']
        read_only_fields = ['id', 'created_at', 'updated_at']
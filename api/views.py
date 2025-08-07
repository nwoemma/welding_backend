from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from django.urls import reverse
from rest_framework.response import Response
from .serializers import UserSerializer,ProfileSerializer,JobSerializer,MaterialSerializer,NotificationSerializer,TaskSerializer,DashboardSerializer
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from accounts.utlity import set_username
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.decorators import permission_classes,authentication_classes
import random
from django.db import models
from django.core.files.base import ContentFile
import base64
from django.utils import timezone
from job_tasks.models import Job, Material,Task, Notification, Application
from accounts.models import User
from datetime import timedelta
from django.core.mail import send_mail
import uuid
from rest_framework.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.conf import settings
import logging
from django.db.utils import OperationalError, ProgrammingError
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_signin(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # Find user by email
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User is not found"}, status=status.HTTP_404_NOT_FOUND)

    # Authenticate user (use username, not email, unless you have a custom backend)
    user = authenticate(request, email=user_obj.email, password=password)
    if not user:
        print("Wrong password or email")
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    # Check admin privileges
    if user.is_superuser or user.is_staff and user.role != 'admin':
        print("User is an admin")
        user.role = 'admin'
        user.save()
    else:
        print("User is not an admin")
        return Response({"error": "You are not authorized to access this resource"}, status=status.HTTP_403_FORBIDDEN)
    # Create token
    token,_ = Token.objects.get_or_create(user=user)
    print('Token has been given')
    return Response({
        "token": token.key,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.get_full_name() or user.username
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_admin(request):
    if not request.user.is_superuser:
        return Response({"error": "Superuser privileges required"}, status=403)
    
    data = request.data.copy()
    data['role'] = 'admin'
    serializer = UserSerializer(data=data)
    
    if serializer.is_valid():
        user = serializer.save(is_staff=True)
        return Response(UserSerializer(user).data, status=201)
    return Response(serializer.errors, status=400)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    print("\n=== DEBUG: REGISTRATION STARTED ===")
    print(f"Raw request data: {request.data}")
    try:
        # Check if the table exists
        from django.apps import apps
        if not apps.is_installed('accounts'):
            return Response({"error": "Accounts app not installed."}, status=500)

        # This avoids trying to query before migrations are applied
        try:
            User.objects.first()
        except Exception as e:
            return Response({"error": "User table inaccessible", "details": str(e)}, status=500)

    except (OperationalError, ProgrammingError) as e:
        print(e)
        return Response({"error": "Database is not ready yet.", "error_detail:":e}, status=500)
    try:
        # Data Extraction and Validation
        full_name = request.data.get('full_name')
        if not full_name:
            print("DEBUG: Missing full_name")
            return Response({"error":"Full name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process names
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Prepare user data
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": request.data.get("email"),
            "phone": request.data.get("phone"),
            "address": request.data.get("address"),
            "role": "client" if request.data.get("role") == "admin" else request.data.get("role"),
            "password": request.data.get("password"),
            "username": set_username(first_name, last_name),
            "is_active": True,  # Activate immediately
            "status": "A"       # Set status to Active
        }

        serializer = UserSerializer(data=user_data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # No activation token needed since we're activating immediately
            user.activation_token = None
            user.activation_expiry = None
            user.save()

            print(f"DEBUG: User registered successfully: {user.email}")
            
            token = Token.objects.create(user=user)
            
            return Response({
                "token": token.key,
                "message": "Registration successful. Your account is now active.",
                "user_id": user.id,
                "email": user.email,
                "is_active": True
            }, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print(f"DEBUG: Registration error: {str(e)}")
        return Response(
            {"error": "Registration failed", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {"error": "Email and Password are both required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        
        if not user.check_password(password):
            return Response(
                {'error': "Invalid password"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        if not user.is_active:
            return Response(
                {'error': "Account not active. Please activate your account."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)
            
    except User.DoesNotExist:
        return Response(
            {'error':'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': "Login failed"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
# 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    Token.objects.filter(user=request.user).delete()
    logout(request)
    return Response({"message": "Logged out successfully."}, status=200)

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def dashboard(request):
    print("AUTH HEADER:", request.META.get("HTTP_AUTHORIZATION"))
    print("User:", request.user)
    print("Is authenticated:", request.user.is_authenticated)
    user = request.user
    jobs = Job.objects.filter(client=user) if user.role == 'client' else Job.objects.all()
    materials = Material.objects.all()  # if 'client' is correct
    notifications = Notification.objects.filter(user=user)
    tasks = Task.objects.filter(job__client=user) if hasattr(user, 'role') and user.role == 'client' else Task.objects.all()
    notification_count = notifications.filter(read=False).count()
    job_count = Job.objects.filter(client=user).count()
    material_count = Material.objects.all().count()
    task_count = Task.objects.filter(job__client=user).count()if hasattr(user, 'role') and user.role == 'client' else Task.objects.all().count()
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    
    dashboard = {}
    dashboard['user'] = user
    dashboard['tasks'] = tasks
    dashboard['jobs'] = jobs
    dashboard['materials'] = materials
    dashboard['job_count'] = job_count
    dashboard['material_count'] = material_count
    dashboard['notification_count'] = notification_count
    dashboard['notifications'] = NotificationSerializer(notifications, many=True).data
    dashboard['task_count'] = task_count
    dashboard['recent_jobs'] = recent_jobs
    if user.role == 'admin':
        dashboard['total_users'] = User.objects.count()
        dashboard['total_jobs'] = Job.objects.count()
        dashboard['total_materials'] = Material.objects.count()
        dashboard['total_notifications'] = Notification.objects.count()
        dashboard['recent_jobs'] = Job.objects.order_by('-created_at')[:5]
        dashboard['active_users'] = User.objects.filter(is_active=True).count()
        dashboard['recent_users'] = User.objects.order_by('-date_joined')[:5]
        dashboard['pending_approvals'] = User.objects.filter(is_active=False).count()

    serializer = DashboardSerializer(dashboard, context= {'request':request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = ProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        data = request.data.copy()
        
        # Handle base64 image if sent
        if 'profile_pic' in data and isinstance(data['profile_pic'], str) and data['profile_pic'].startswith('data:image'):
            format, imgstr = data['profile_pic'].split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"profile_{user.id}.{ext}"
            user.profile_pic.save(file_name, ContentFile(base64.b64decode(imgstr)))
            data.pop('profile_pic')  # Remove from data since we've handled it
        
        serializer = ProfileSerializer(user, data=data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            # Handle nested data
            if 'social' in data:
                user.social = data['social']
            if 'notifications' in data:
                user.notifications = data['notifications']
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seen_jobs(request):
    user = request.user
    jobs = Job.objects.filter(welder=user)
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_list(request):
    jobs = Job.objects.all().select_related('client', 'welder')
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    if request.method == 'GET':
        serializer = JobSerializer(job)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = JobSerializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    role = request.query_params.get('role', '').lower()
    users = User.objects.all()
    
    if role == 'client':
        users = users.filter(groups__name='Client')
    elif role == 'welder':
        users = users.filter(groups__name='Welder')
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_search(request):
    queryset = Job.objects.all().select_related('client', 'welder')
    
    # Search parameters
    search = request.query_params.get('search', None)
    status_filter = request.query_params.get('status', None)
    
    if search:
        queryset = queryset.filter(
            models.Q(job_id__icontains=search) |
            models.Q(job_type__icontains=search) |
            models.Q(description__icontains=search)
        )
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    serializer = JobSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_list_paginated(request):
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    jobs = Job.objects.all().select_related('client', 'welder')
    result_page = paginator.paginate_queryset(jobs, request)
    
    serializer = JobSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_job(request):
#     serializer = JobSerializer(data=request.data)
#     if serializer.is_valid():
#         job = serializer.save()
#         return Response(JobSerializer(job).data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job(request):
    job_id = request.data.get('job_id')
    job_type = request.data.get('job_type')
    description = request.data.get('description')
    deadline = request.data.get('deadline')
    
    job_data = {
        'job_id':job_id,
        'job_type':job_type,
        'descriptions': description,
        'deadline':deadline
    }
    serializer = JobSerializer(data=job_data)
    if serializer.is_valid():
        job = serializer.save()
     
    
        token = Token.objects.create(job)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def apply_for_job(request, user_id, job_id):
    firstname = request.data.get('first_name')
    lastname = request.data.get('last_name')
    email = request.data.get('email')
    phone = request.data.get('phone')
    resume = request.FILES.get('resume')
    cover_letter = request.data.get('cover_letter')
    experience = request.data.get('experience')
    education = request.data.get('education')
    skills = request.data.get('skills')
    source = request.data.get('source', 'website')

    if not all([firstname, lastname, email, phone, resume, cover_letter, experience, education, skills, source]):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)
    if not request.user.is_authenticated:
        return Response({"error": "You must be logged in to apply for a job."}, status=status.HTTP_401_UNAUTHORIZED)

    user = get_object_or_404(User, id=user_id)
    if user.role != 'welder':
        return Response({"error": "Only welders can apply for jobs."}, status=status.HTTP_403_FORBIDDEN)
    
    
    job = get_object_or_404(Job, id=job_id)

    if job.status not in Job.STATUS_CHOICES:
        return Response({"error": "Job is not open for applications."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if the welder has already applied
    if job.welder == user:
        return Response({"error": "You have already applied for this job."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Assign the welder to the job
    job.welder = user
    job.status = 'in_progress'
    job.save()
    
    return Response({"message": "You have successfully applied for the job."}, status=status.HTTP_200_OK)
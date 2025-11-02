from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from django.urls import reverse
from rest_framework.response import Response
from .serializers import UserSerializer,ProfileSerializer,JobSerializer,MaterialSerializer,NotificationSerializer,TaskSerializer,DashboardSerializer, ReportIssueSerializer, LogWorkSerializer
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
from django.utils import timezone
from job_tasks.models import Job, LogWork, Material,Task, Notification, Application
from django.core.exceptions import ValidationError
import magic
from accounts.models import User
from datetime import timedelta
from django.core.mail import send_mail
import uuid
from rest_framework.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.conf import settings
import logging
from accounts.models import UserManager
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
    unread_notification_count = notifications.filter(read=False).count()
    total_users = User.objects.all().count()
    total_jobs = Job.objects.filter(welder=user).all()
    pending_count = Job.objects.filter(status="Pending")
    job_count = Job.objects.filter(client=user).count()
    material_count = Material.objects.all().count()
    total_notifications = Notification.objects.all().count()
    task_count = Task.objects.filter(job__client=user).count()if hasattr(user, 'role') and user.role == 'client' else Task.objects.all().count()
    active_users = User.objects.filter(status="active")[:5]
    recent_users = User.objects.order_by('-created_at')[:5]
    recent_jobs = Job.objects.all()[:5]
    dashboard = {}
    dashboard['user'] = user
    dashboard['tasks'] = tasks
    dashboard['jobs'] = jobs
    dashboard['materials'] = materials
    dashboard['job_count'] = job_count
    dashboard['material_count'] = material_count
    dashboard['unread_notifications_count'] = unread_notification_count
    dashboard['notifications'] = notifications
    dashboard['unread_notification_count']= unread_notification_count
    dashboard['total_users'] = total_users
    dashboard['total_jobs'] = total_jobs
    dashboard['recent_jobs'] = recent_jobs
    dashboard['pending_count'] = pending_count
    dashboard['task_count'] = task_count
    dashboard['active_users'] = active_users
    dashboard['recent_users'] = recent_users
    dashboard['total_notifications'] = total_notifications
    serializer = DashboardSerializer(dashboard, context= {'request':request})
    return Response(serializer.data, status=status.HTTP_200_OK)
@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile_view(request):
    try:
        user = request.user
        logger.info(f"Profile request from user: {user.email}")
        
        if request.method == 'GET':
            serializer = ProfileSerializer(user)
            return Response(serializer.data)
            
        elif request.method == 'PUT':
            data = request.data.copy()
            logger.debug(f"Received profile update data: {data}")
            
            if 'profile_pic' in request.FILES:
                data['profile_pic'] = request.FILES['profile_pic']
                logger.info("Profile picture file received")
            
            serializer = ProfileSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info("Profile updated successfully")
                return Response(serializer.data)
            
            logger.error(f"Profile update validation errors: {serializer.errors}")
            return Response(serializer.errors, status=400)
            
    except Exception as e:
        logger.error(f"Profile view error: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)

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
@permission_classes([IsAuthenticated])
def apply_for_job(request, job_id):
    # Validate user is a welder
    if request.user.role != 'welder':
        return Response(
            {"error": "Only welders can apply for jobs"}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # Get job instance
    job = get_object_or_404(Job, id=job_id)

    # Check for existing application
    if Application.objects.filter(user=request.user, job=job).exists():
        return Response(
            {"error": "You have already applied to this job"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate required fields
    required_fields = {
        'first_name': request.data.get('first_name'),
        'last_name': request.data.get('last_name'),
        'email': request.data.get('email'),
        'phone': request.data.get('phone'),
        'resume': request.FILES.get('resume'),
        'experience': request.data.get('experience'),
        'education': request.data.get('education'),
        'skills': request.data.get('skills')
    }

    missing_fields = [field for field, value in required_fields.items() if not value]
    if missing_fields:
        return Response(
            {"error": f"Missing required fields: {', '.join(missing_fields)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate file type and size
    resume = required_fields['resume']
    try:
        file_type = magic.from_buffer(resume.read(1024), mime=True)
        resume.seek(0)  # Reset file pointer
        
        if file_type not in ['application/pdf', 'application/msword', 
                            'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            raise ValidationError("Only PDF or Word documents are allowed")
        
        if resume.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationError("File size exceeds 5MB limit")
            
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create application
    try:
        application = Application.objects.create(
            job=job,
            user=request.user,
            first_name=required_fields['first_name'],
            last_name=required_fields['last_name'],
            email=required_fields['email'],
            phone=required_fields['phone'],
            resume=resume,
            cover_letter=request.data.get('cover_letter', ''),
            experience=required_fields['experience'],
            education=required_fields['education'],
            skills=required_fields['skills'],
            source=request.data.get('source', 'website')
        )
        
        return Response(
            {
                "success": "Application submitted successfully",
                "application_id": application.id,
                "status": application.status
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        return Response(
            {"error": "Failed to process application"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['POST'])
def reject_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)

    if application.status != 'submitted':
        return Response(
            {"error": "Only submitted applications can be withdrawn"},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    if request.user.role == "welder":
        return Response(
            {"error": "Welder cannot withdraw application"},
            status=status.HTTP_400_BAD_REQUEST
        )

    application.status = 'rejected'
    application.save()

    return Response(
        {"success": "Application rejected successfully"},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
def issue_report(request):
    reported_by = request.user
    title = request.data.get('title')
    description = request.data.get('description')

    # Validate required fields
    if not title or not description:
        return Response(
            {"error": "Missing required fields"},
            status=status.HTTP_400_BAD_REQUEST
        )
    data = {
        "title": title,
        "description": description,
        "reported_by": reported_by
    }

    serializer = ReportIssueSerializer(data=data)
    if serializer.is_valid():
        issue = serializer.save()
        return Response(
            {"success": "Issue reported successfully", "issue_id": issue.id},
            status=status.HTTP_201_CREATED
        )
    return Response(
        {"error": "Failed to report issue"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
@api_view(['GET'])
def see_log_work(request):
    user = request.user
    log_entries = LogWork.objects.filter(user=user)
    serializer = LogWorkSerializer(log_entries, many=True)
    return Response(serializer.data)

@api_view(["GET", "POST"])
def see_job_materials(request):
    job_id = request.query_params.get("job_id")
    if not job_id:
        return Response(
            {"error": "Job ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    materials = Material.objects.filter(job__id=job_id)
    serializer = MaterialSerializer(materials, many=True)
    return Response(serializer.data)
    
def add_job_materials(request):
    data = {
        "name":request.data.get('name'),
        'quantity': request.data.get('quantity'),
        'cost': request.data.get('cost')    
    }
    serializer = MaterialSerializer(data=data)
    if serializer.is_valid():
        material = serializer.save()
        return Response(
            {"success": "Material added successfully", "material_id": material.id},
            status=status.HTTP_201_CREATED
        )
    return Response(
        {"error": "Failed to add material"},
        status=status.HTTP_400_BAD_REQUEST
    )
from django.urls import path
from api import views

urlpatterns = [
    path('sign_up/', views.register, name='register'),
    path("sign_in/", views.login_user, name="signin"),
    # path('get_dashboard_data/', views.get_dashboard_data, name="get_dashboard_data")
    path('dashboard/', views.dashboard, name="dashboard"),
    path('profile/', views.profile_view, name="profile"),
    path('admin/signin/', views.admin_signin, name='admin_signin'),
    path('job_create/',views.create_job, name="job_create"),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/search/', views.job_search, name='job_search'),
    path('jobs/paginated/', views.job_list_paginated, name='job_list_paginated'),
    path('users/', views.user_list, name='user-list'),
    path('apply_for_job/<int:job_id>/<str:user_id>/', views.apply_for_job, name='apply_for_job'),
]

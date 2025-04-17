from django.urls import path
from . import views
from .views import SubmissionDetailView

urlpatterns = [
    path('subject/create/', views.subject_create, name='subject_create'),
    path('teacher/create/', views.teacher_create, name='teacher_create'),
    path('group/create/', views.group_create, name='group_create'),
    path('student/create/', views.student_create, name='student_create'),
    path('student-subjects/', views.student_subjects, name='student_subjects'),
    path('about-subjects/', views.about_subjects, name='about_subjects'),
    path('add-User/', views.add_user, name='add-user'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('groups/create/', views.create_group, name='create_group'),
    path('tasks/create/', views.create_or_update_task, name='create_task'),
    path('task/<int:task_id>/update/', views.create_or_update_task, name='update_task'),
    path('ajax/load-groups/', views.load_groups, name='load_groups'),
    path('ajax/validate-group/', views.validate_group, name='validate_group'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:pk>/submit/', views.submit_task, name='submit_task'),
    path('task/<int:pk>/submission_detail/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('', views.main, name='main'),
]
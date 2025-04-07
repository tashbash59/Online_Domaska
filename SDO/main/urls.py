from django.urls import path
from . import views

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
    path('tasks/create/', views.create_task, name='create_task'),
    path('ajax/load-groups/', views.load_groups, name='load_groups'),
    path('ajax/validate-group/', views.validate_group, name='validate_group'),
    path('', views.main, name='main'),
]
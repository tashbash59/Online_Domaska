from django.urls import path
from . import views

urlpatterns = [
    path('subject/create/', views.subject_create, name='subject_create'),
    path('teacher/create/', views.teacher_create, name='teacher_create'),
    path('group/create/', views.group_create, name='group_create'),
    path('student/create/', views.student_create, name='student_create'),
    path('student-subjects/', views.student_subjects, name='student_subjects'),
    path('about-subjects/', views.about_subjects, name='about_subjects'),
]
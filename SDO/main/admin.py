from django.contrib import admin
from .models import Subject, Teacher, Group, Student, Role, Task, TaskSubmission


admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Role)
admin.site.register(Task)
admin.site.register(TaskSubmission)

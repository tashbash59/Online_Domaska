from django.contrib import admin
from .models import Subject, Teacher, Group, Student


admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Group)
admin.site.register(Student)
from django import forms
from .models import Subject, Teacher, Group, Student

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'teacher', 'group','description']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        if Group.objects.filter(name=name).exists():
            raise forms.ValidationError("Группа с таким именем уже существует.")
        return name

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'group']
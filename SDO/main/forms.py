from django import forms
from .models import Subject, Teacher, Group, Student,User, Role
import random
import string


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

def generate_unique_username(name):
    base_username = name.lower().replace(' ', '_')
    unique_id = ''.join(random.choices(string.digits, k=4))  # Добавляем 4 случайные цифры
    return f"{base_username}_{unique_id}"


class UserForm(forms.Form):
    name = forms.CharField(max_length=255, label='Имя')
    role = forms.ModelChoiceField(queryset=Role.objects.all(), label='Роль')

    def save(self):
        # Генерация логина и пароля
        name = self.cleaned_data['name']
        role = self.cleaned_data['role']

        # Генерация логина (например, имя в нижнем регистре без пробелов)
        login = generate_unique_username(name)
        # Генерация пароля (например, случайная строка)
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Создание пользователя
        user = User.objects.create_user(username=login, password=password)
        user.role = role
        user.plain_password = password
        user.save()

        # Создание записи в таблице Student или Teacher в зависимости от роли
        if role.name == 'Студент':
            Student.objects.create(user=user, name=name)
        elif role.name == 'Преподаватель':
            Teacher.objects.create(user=user, name=name)

        return user
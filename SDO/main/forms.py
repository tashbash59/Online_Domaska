from django import forms
from .models import Subject, Teacher, Group, Student,User, Role
from django.contrib.auth.forms import AuthenticationForm
import random
import string
from main.utils.letters import convert_fio_to_english


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
    name = forms.CharField(
        label='ФИО (полностью кириллицей)',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пример: Иванов Иван Иванович'
        }),
        help_text='Введите фамилию, имя и отчество через пробел')
    role = forms.ModelChoiceField(queryset=Role.objects.all(), label='Роль')


    def save(self):
        # Генерация логина и пароля
        name = convert_fio_to_english(self.cleaned_data['name'])
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


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
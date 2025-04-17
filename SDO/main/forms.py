from django import forms
from .models import Subject, Teacher, Group, Student,User, Role, Task, TaskSubmission
from django.contrib.auth.forms import AuthenticationForm
import random
import string
from main.utils.letters import convert_fio_to_english
from django.utils import timezone


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'teacher', 'groups', 'description']  # Заменили group на groups
        widgets = {
            'groups': forms.SelectMultiple(attrs={'class': 'form-control'})  # Для множественного выбора
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если нужно фильтровать группы для преподавателя
        if 'teacher' in kwargs:
            teacher = kwargs['teacher']
            self.fields['groups'].queryset = Group.objects.filter(
                subjects__teacher=teacher
            ).distinct()
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
            'placeholder': 'ФИО полностью'
        }),
        help_text='Введите фамилию, имя и отчество через пробел')
    role = forms.ModelChoiceField(queryset=Role.objects.all(), label='Роль')
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label='Группа')


    def save(self):
        # Генерация логина и пароля
        name = self.cleaned_data['name']
        print(name)
        login_name = convert_fio_to_english(name)
        role = self.cleaned_data['role']
        group = self.cleaned_data['group']

        # Генерация логина (например, имя в нижнем регистре без пробелов)
        login = generate_unique_username(login_name)
        # Генерация пароля (например, случайная строка)
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Создание пользователя
        user = User.objects.create_user(username=login, password=password)
        user.role = role
        user.plain_password = password
        user.save()

        # Создание записи в таблице Student или Teacher в зависимости от роли
        if role.name == 'Студент':
            Student.objects.create(user=user, name=name,group=group)
        elif role.name == 'Преподаватель':
            Teacher.objects.create(user=user, name=name)

        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class GroupCreateForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(group__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Студенты без группы'
    )

    class Meta:
        model = Group
        fields = ['name', 'students']
        labels = {
            'name': 'Название группы'
        }


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'subject', 'group', 'deadline','file']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Введите название',
                'class': 'title-placeholder',
                'style': 'font-size: 24px; font-weight: bold;'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Введите описание задачи, чтобы студентам было проще разобраться в нём',
                'rows': 4,
                'id': 'description-textarea',
                'class': 'description-placeholder',
                'style': 'font-size: 16px; font-weight: normal;'
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_subject'  # Добавляем ID для JavaScript
            }),
            'group': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_group'  # Добавляем ID для JavaScript
            }),
            'file': forms.FileInput(attrs={
                'class': 'file-input',
                'id': 'file-upload'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
        if teacher:
            # Фильтруем предметы по преподавателю
            self.fields['subject'].queryset = teacher.subject_set.all()
            
            # Инициализируем queryset для групп как пустой
            self.fields['group'].queryset = Group.objects.filter(
                subjects__teacher=teacher
            ).distinct()
            
            # Если форма привязана к существующему объекту
            if self.instance.pk and self.instance.subject:
                # Обновляем queryset групп для выбранного предмета
                self.fields['group'].queryset = self.instance.subject.groups.all()
    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        group = cleaned_data.get('group')
        
        if subject and group:
            if not subject.groups.filter(id=group.id).exists():
                self.add_error('group', 'Выбранная группа не преподается для этого предмета')
        
        return cleaned_data

class TaskSubmissionForm(forms.Form):
    solution = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Введите ваше решение здесь...'
        }),
        required=True,
        label='Текстовое решение'
    )
    
    solution_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file'
        }),
        required=False,
        label='Файл с решением (необязательно)'
    )

class GradeForm(forms.ModelForm):
    class Meta:
        model = TaskSubmission
        fields = ['grade', 'teacher_comment']
        widgets = {
            'grade': forms.NumberInput(attrs={
                'min': 1,
                'max': 100,
                'class': 'form-control'
            }),
            'teacher_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }
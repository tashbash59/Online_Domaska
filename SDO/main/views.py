from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Subject, Teacher, Group, Student, User
from .forms import SubjectForm, TeacherForm, GroupForm, StudentForm,UserForm,GroupCreateForm
from django.contrib import messages

@login_required(login_url='login')
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Предмет успешно добавлен!')
            return redirect('subject_create')
    else:
        form = SubjectForm()
    subjects = Subject.objects.select_related('teacher', 'group').all()
    return render(request, 'main/subject_form.html', {'form': form, 'subjects': subjects})

@login_required(login_url='login')
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Прпеподаватель успешно добавлен!')
            return redirect('teacher_create')
    else:
        form = TeacherForm()
    teacher = Teacher.objects.all()
    return render(request, 'main/teacher_form.html', {'form': form, 'teachers': teacher})


@login_required(login_url='login')
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Группа успешно добавлена!')
                return redirect('group_create')
            except IntegrityError:
                print('Группа с таким именем уже существует.')
    else:
        form = GroupForm()

    subjects = Group.objects.all()
    return render(request, 'main/group_form.html', {'form': form, 'subjects': subjects})


@login_required(login_url='login')
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Студент успешно добавлен!')
            return redirect('student_create')
    else:
        form = StudentForm()
    students = Student.objects.select_related('group').all()
    return render(request, 'main/student_form.html', {'form': form, 'students': students})

@login_required(login_url='login')
def student_subjects(request):
    students = Student.objects.all()  # Получаем всех студентов
    student_id = request.GET.get('student_id')
    selected_student = get_object_or_404(Student, id=student_id)
    subjects = Subject.objects.filter(group=selected_student.group)

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        selected_student = get_object_or_404(Student, id=student_id)
        subjects = Subject.objects.filter(group=selected_student.group)  # Получаем предметы группы студента

    return render(request, 'main/subject_list.html', {
        'students': students,
        'selected_student': selected_student,
        'subjects': subjects,
    })

@login_required(login_url='login')
def about_subjects(request):
	subject_id = request.GET.get('subject_id')
	subjects = get_object_or_404(Subject, id=subject_id)
	return render(request, 'main/about_subject.html', {'subjects': subjects})


@login_required(login_url='login')
def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('add-user')  # Замените 'user_list' на имя вашего URL
    else:
        form = UserForm()

    students = Student.objects.all()
    teachers = Teacher.objects.all()

    return render(request, 'main/add_user.html', {
        'form': form,
        'students': students,
        'teachers': teachers,
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main')  # Перенаправление на главную страницу после успешного входа
    else:
        form = AuthenticationForm()

    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def main(request):
    user = request.user
    role_name = user.get_role_name()
    return render(request, 'main/main.html', {'role_name': role_name})



def create_group(request):
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save()
            # Назначаем выбранных студентов в группу
            students = form.cleaned_data['students']
            students.update(group=group)
            return redirect('create_group')  # Перенаправляем на список групп
    else:
        form = GroupCreateForm()
    
    return render(request, 'main/create_group.html', {'form': form})
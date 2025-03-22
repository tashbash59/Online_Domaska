from django.shortcuts import render, get_object_or_404, redirect
from .models import Subject, Teacher, Group, Student, User
from .forms import SubjectForm, TeacherForm, GroupForm, StudentForm,UserForm
from django.contrib import messages

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

def about_subjects(request):
	subject_id = request.GET.get('subject_id')
	subjects = get_object_or_404(Subject, id=subject_id)
	return render(request, 'main/about_subject.html', {'subjects': subjects})


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
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone 
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from main.utils.letters import convert_to_short_name
from .models import Subject, Teacher, Group, Student, User, Task, TaskSubmission
from .forms import SubjectForm, TeacherForm, GroupForm, StudentForm,UserForm,GroupCreateForm,TaskCreateForm,TaskSubmissionForm
from django.contrib import messages
from django.http import JsonResponse,HttpResponseForbidden
from django.views.generic import FormView
from .forms import GradeForm
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse


@login_required(login_url='login')
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.save()
            form.save_m2m()  # Важно для сохранения ManyToMany связей
            messages.success(request, 'Предмет успешно добавлен!')
            return redirect('subject_create')
    else:
        form = SubjectForm()
    
    # Изменяем запрос для получения предметов
    subjects = Subject.objects.select_related('teacher').prefetch_related('groups').all()
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
    students = Student.objects.all()
    student_id = request.GET.get('student_id')
    
    if student_id:
        selected_student = get_object_or_404(Student, id=student_id)
        # Изменяем запрос для ManyToMany связи
        subjects = Subject.objects.filter(groups=selected_student.group)
    else:
        selected_student = None
        subjects = None

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        selected_student = get_object_or_404(Student, id=student_id)
        subjects = Subject.objects.filter(groups=selected_student.group)

    return render(request, 'main/subject_list.html', {
        'students': students,
        'selected_student': selected_student,
        'subjects': subjects,
    })

@login_required(login_url='login')
def about_subjects(request):
    subject_id = request.GET.get('subject_id')
    subject = get_object_or_404(Subject.objects.prefetch_related('groups'), id=subject_id)
    return render(request, 'main/about_subject.html', {'subject': subject})


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
    
    context = {'role_name': role_name}
    today = timezone.now().date()
    
    if role_name == 'Преподаватель':
        try:
            teacher = request.user.teacher
            tasks = Task.objects.filter(teacher=teacher).order_by('-created_at')
            urgent_tasks = []
            
            for task in tasks:
                created_date = task.created_at.date() if hasattr(task.created_at, 'date') else task.created_at
                deadline = task.deadline
                task.teacher_short_name = convert_to_short_name(task.teacher.name)
                if deadline and deadline < today:
                        task.status = "Просрочено"
                        task.status_class = "overdue"
                elif created_date == today or (today - created_date).days <= 1:
                    if deadline and (deadline - today).days <= 2:
                        task.status = "Скоро дедлайн"
                        task.status_class = "deadline-soon"
                    else:
                        task.status = "Новое"
                        task.status_class = "new"
                else:
                    task.status = "В работе"
                    task.status_class = "in-progress"

                if task.status == "Скоро дедлайн":
                    urgent_tasks.append(task)

            context.update({
                'tasks': tasks,
                'urgent_tasks': urgent_tasks
            })

        except Teacher.DoesNotExist:
            pass
    
    elif role_name == 'Студент':
        try:
            student = request.user.student
            if student.group:
                # Получаем задачи для группы студента
                tasks = Task.objects.filter(group=student.group).order_by('-created_at')
                student_tasks = []
                urgent_tasks = []
                
                for task in tasks:
                    created_date = task.created_at.date() if hasattr(task.created_at, 'date') else task.created_at
                    deadline = task.deadline
                    task.teacher_short_name = convert_to_short_name(task.teacher.name)

                    if deadline and deadline < today:
                        task.status = "Просрочено"
                        task.status_class = "overdue"
                    elif created_date == today or (today - created_date).days <= 1:
                        if deadline and (deadline - today).days <= 2:
                            task.status = "Скоро дедлайн"
                            task.status_class = "deadline-soon"
                            urgent_tasks.append(task)
                        else:
                            task.status = "Новое"
                            task.status_class = "new"
                    else:
                        task.status = "В работе"
                        task.status_class = "in-progress"
                    
                    student_tasks.append(task)

                context.update({
                    'tasks': student_tasks,
                    'urgent_tasks': urgent_tasks
                })
                
        except Student.DoesNotExist:
            pass
    
    if role_name == 'Преподаватель':
        # Добавьте список предметов в контекст
        context['subjects'] = request.user.teacher.subject_set.all()
    elif role_name == 'Студент':
        # Для студентов тоже можно добавить предметы
        context['subjects'] = Subject.objects.filter(groups=request.user.student.group)
    
    return render(request, 'main/main.html', context)

@login_required
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

# @login_required
# def create_task(request):
#     try:
#         teacher = request.user.teacher
#     except Teacher.DoesNotExist:
#         return HttpResponseForbidden("Доступ только для преподавателей")

#     if request.method == 'POST':
#         form = TaskCreateForm(request.POST, request.FILES, teacher=teacher)
#         if form.is_valid():
#             task = form.save(commit=False)
#             task.teacher = teacher
#             task.save()
#             return redirect('main')
#         print(form.errors)
#     else:
#         form = TaskCreateForm(teacher=teacher)

#     return render(request, 'main/create_task.html', {'form': form})


@login_required
def create_or_update_task(request, task_id=None):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return HttpResponseForbidden("Доступ только для преподавателей")

    # Если передан task_id, значит это редактирование существующей задачи
    task = None
    if task_id:
        task = get_object_or_404(Task, id=task_id, teacher=teacher)

    if request.method == 'POST':
        form = TaskCreateForm(request.POST, request.FILES, teacher=teacher, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.teacher = teacher
            task.save()
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskCreateForm(teacher=teacher, instance=task)

    context = {
        'form': form,
        'is_edit': task is not None,
    }
    return render(request, 'main/create_task.html', context)

@login_required
@require_GET
def load_groups(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return JsonResponse({'error': 'Доступ только для преподавателей'}, status=403)
    
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'groups': []})
    
    try:
        # Изменяем запрос для ManyToMany связи
        groups = Group.objects.filter(
            subjects__id=subject_id,
            subjects__teacher=teacher
        ).distinct().values('id', 'name')
        return JsonResponse({'groups': list(groups)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_GET
def validate_group(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return JsonResponse({'error': 'Доступ только для преподавателей'}, status=403)
    
    subject_id = request.GET.get('subject_id')
    group_id = request.GET.get('group_id')
    
    if not subject_id or not group_id:
        return JsonResponse({'valid': False})
    
    try:
        # Изменяем проверку для ManyToMany связи
        valid = Group.objects.filter(
            id=group_id,
            subjects__id=subject_id,
            subjects__teacher=teacher
        ).exists()
        return JsonResponse({'valid': valid})
    except Exception as e:
        return JsonResponse({'valid': False, 'error': str(e)})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    today = timezone.now().date()
    user = request.user
    role_name = user.get_role_name()
    
    # Определяем статус текущей задачи
    created_date = task.created_at.date() if hasattr(task.created_at, 'date') else task.created_at
    deadline = task.deadline
    
    if deadline and deadline < today:
        task.status = "Просрочено"
        task.status_class = "overdue"
    elif created_date == today or (today - created_date).days <= 1:
        if deadline and (deadline - today).days <= 2:
            task.status = "Скоро дедлайн"
            task.status_class = "deadline-soon"
        else:
            task.status = "Новое"
            task.status_class = "new"
    else:
        task.status = "В работе"
        task.status_class = "in-progress"
    
    # Добавляем короткое имя преподавателя
    task.teacher_short_name = convert_to_short_name(task.teacher.name)
    
    # Подготовка контекста
    context = {
        'task': task,
        'role_name': role_name,
        'today': today
    }
    
    # Логика для преподавателя
    if role_name == 'Преподаватель':
        try:
            teacher = request.user.teacher
            # Все задачи преподавателя (кроме текущей)
            tasks = Task.objects.filter(teacher=teacher).exclude(id=task_id).order_by('-created_at')
            urgent_tasks = []
            
            for t in tasks:
                t.created_date = t.created_at.date() if hasattr(t.created_at, 'date') else t.created_at
                if t.deadline and t.deadline < today:
                    t.status = "Просрочено"
                    t.status_class = "overdue"
                elif t.created_date == today or (today - t.created_date).days <= 1:
                    if t.deadline and (t.deadline - today).days <= 2:
                        t.status = "Скоро дедлайн"
                        t.status_class = "deadline-soon"
                        urgent_tasks.append(t)
                    else:
                        t.status = "Новое"
                        t.status_class = "new"
                else:
                    t.status = "В работе"
                    t.status_class = "in-progress"
                
                t.teacher_short_name = convert_to_short_name(t.teacher.name)

            # Получаем все сдачи для текущего задания
            task_submissions = TaskSubmission.objects.filter(task=task).select_related('student')
            
            context.update({
                'tasks': tasks,
                'urgent_tasks': urgent_tasks,
                'subjects': teacher.subject_set.all(),
                'task_submissions': task_submissions  # Добавляем сдачи в контекст
            })

        except Teacher.DoesNotExist:
            pass
    
    # Логика для студента
    elif role_name == 'Студент':
        try:
            student = request.user.student
            if student.group:
                # Все задачи группы студента (кроме текущей)
                tasks = Task.objects.filter(group=student.group).exclude(id=task_id).order_by('-created_at')
                student_tasks = []
                urgent_tasks = []
                
                for t in tasks:
                    t.created_date = t.created_at.date() if hasattr(t.created_at, 'date') else t.created_at
                    if t.deadline and t.deadline < today:
                        t.status = "Просрочено"
                        t.status_class = "overdue"
                    elif t.created_date == today or (today - t.created_date).days <= 1:
                        if t.deadline and (t.deadline - today).days <= 2:
                            t.status = "Скоро дедлайн"
                            t.status_class = "deadline-soon"
                            urgent_tasks.append(t)
                        else:
                            t.status = "Новое"
                            t.status_class = "new"
                    else:
                        t.status = "В работе"
                        t.status_class = "in-progress"
                    
                    t.teacher_short_name = convert_to_short_name(t.teacher.name)
                    student_tasks.append(t)

                # Получаем сдачу текущего студента для этой задачи
                task_submission = TaskSubmission.objects.filter(task=task, student=student).first()
                
                context.update({
                    'tasks': student_tasks,
                    'urgent_tasks': urgent_tasks,
                    'subjects': Subject.objects.filter(groups=student.group),
                    'task_submission': task_submission  # Добавляем сдачу студента
                })
                
        except Student.DoesNotExist:
            pass
    
    # Проверка доступа
    if role_name == 'Преподаватель' and task.teacher != request.user.teacher:
        raise Http404
    elif role_name == 'Студент' and task.group != request.user.student.group:
        raise Http404
    
    return render(request, 'main/task_about.html', context)


@login_required
def submit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Только студенты могут сдавать задания')
        return redirect('task_detail', task_id=pk)
    
    if request.method == 'POST':
        form = TaskSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # Создаем или обновляем сдачу задания
            TaskSubmission.objects.update_or_create(
                task=task,
                student=request.user.student,
                defaults={
                    'solution': form.cleaned_data['solution'],
                    'solution_file': form.cleaned_data['solution_file']
                }
            )
            messages.success(request, 'Решение успешно отправлено!')
            return redirect('task_detail', task_id=pk)
    else:
        # Пробуем загрузить существующее решение
        try:
            submission = TaskSubmission.objects.get(task=task, student=request.user.student)
            initial_data = {
                'solution': submission.solution,
                'solution_file': submission.solution_file
            }
            form = TaskSubmissionForm(initial=initial_data)
        except TaskSubmission.DoesNotExist:
            form = TaskSubmissionForm()
    
    return render(request, 'main/submit_task.html', {
        'form': form,
        'task': task
    })


class SubmissionDetailView(LoginRequiredMixin, DetailView):
    model = TaskSubmission
    template_name = 'main/submission_detail.html'
    context_object_name = 'submission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = GradeForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = GradeForm(request.POST, instance=self.object)
        
        if form.is_valid():
            if form.cleaned_data.get('grade'):
                self.object.status = 'graded'
            form.save()
            return redirect(reverse('task_detail', kwargs={'task_id': self.object.task.id}))
        
        return self.render_to_response(self.get_context_data(form=form))
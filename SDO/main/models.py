from django.db import models
from django.contrib.auth.models import AbstractUser,  Group, Permission


class Role(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название роли', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Роль', null=True, blank=True)
    plain_password = models.CharField(max_length=128, blank=True, null=True, verbose_name='Пароль (открытый)')

    groups = models.ManyToManyField(
        Group,
        verbose_name='Группы',
        blank=True,
        related_name='main_user_set',  # Уникальный related_name
        related_query_name='main_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='Права доступа',
        blank=True,
        related_name='main_user_set',  # Уникальный related_name
        related_query_name='main_user',
    )

    def get_role_name(self):
        if self.role:
            return self.role.name
        return "Роль не указана"
    
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь', null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name='ФИО')

    def get_role(self):
        return self.user.role.name

    def get_login(self):
        return self.user.username

    def get_password(self):
        return self.user.plain_password

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

class Group(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название',unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Преподаватель')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    description = models.CharField(max_length=255, verbose_name='Описание',null=True,  # Разрешает NULL в базе данных
        blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь', null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name='ФИО')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа',null=True,blank=True)

    def get_role(self):
        return self.user.role.name

    def get_login(self):
        return self.user.username

    def get_password(self):
        return self.user.plain_password

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'


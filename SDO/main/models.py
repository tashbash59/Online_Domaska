from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=255, verbose_name='ФИО')

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
    name = models.CharField(max_length=255, verbose_name='ФИО')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
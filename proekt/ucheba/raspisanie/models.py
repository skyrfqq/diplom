from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator


class Profile(models.Model):
    """
    Профиль пользователя, расширяющий стандартную модель User.
    
    Поля:
    - user: связь один-к-одному с моделью User (стандартная модель пользователя Django)
    - role: роль пользователя (студент/преподаватель/администратор)
    - group: связь с группой (только для студентов)
    
    Методы:
    - __str__: возвращает строковое представление в формате "username (роль)"
    """
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Группа', related_name='student_profiles')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Group(models.Model):
    """
    Модель учебной группы.
    
    Поля:
    - name: название группы (уникальное)
    - students: связь многие-ко-многим с User через Profile
    
    Методы:
    - __str__: возвращает название группы
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='Название группы')
    students = models.ManyToManyField(User, through=Profile, related_name='study_groups')

    def __str__(self):
        return self.name


class Room(models.Model):
    """
    Модель учебной аудитории.
    
    Поля:
    - number: номер аудитории (уникальный)
    - capacity: вместимость аудитории (количество мест)
    
    Методы:
    - __str__: возвращает номер аудитории
    """
    number = models.CharField(max_length=20, unique=True, verbose_name='Номер кабинета')
    capacity = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.number


class Subject(models.Model):
    """
    Модель учебного предмета.
    
    Поля:
    - name: название предмета
    - teacher: связь с преподавателем (User)
    
    Методы:
    - __str__: возвращает название предмета
    """
    name = models.CharField(max_length=100, verbose_name='Название предмета')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')

    def __str__(self):
        return self.name


class Schedule(models.Model):
    """
    Модель расписания занятий.
    
    Поля:
    - group: связь с группой
    - subject: связь с предметом
    - teacher: связь с преподавателем (Profile)
    - day: день недели (пн-сб)
    - time: время занятия
    - date: конкретная дата (опционально)
    
    Методы:
    - __str__: возвращает строковое представление занятия
    """
    DAYS = [
        ('mon', 'Понедельник'),
        ('tue', 'Вторник'),
        ('wed', 'Среда'),
        ('thu', 'Четверг'),
        ('fri', 'Пятница'),
        ('sat', 'Суббота'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    teacher = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, verbose_name='Преподаватель')
    day = models.CharField(max_length=3, choices=DAYS, verbose_name='День недели')
    time = models.CharField(max_length=20, verbose_name='Время')
    date = models.DateField(null=True, blank=True, verbose_name='Дата')

    def __str__(self):
        return f"{self.group} | {self.subject} | {self.teacher} | {self.day} {self.time} {self.date or ''}"


class LoginLog(models.Model):
    """
    Модель для логирования входов пользователей в систему.
    
    Поля:
    - user: связь с пользователем
    - login_time: время входа (автоматически заполняется)
    
    Методы:
    - __str__: возвращает строковое представление входа
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} вошёл {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}"

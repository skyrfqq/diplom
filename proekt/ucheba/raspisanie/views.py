from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from .models import Profile, Group, Room, Subject, Schedule, LoginLog
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate
from django.db.models import Count

def is_admin(user):
    """
    Проверяет, является ли пользователь администратором.
    Проверка осуществляется через наличие профиля и роль 'admin'.
    """
    return hasattr(user, 'profile') and user.profile.role == 'admin'

def admin_required(view_func):
    """
    Декоратор для проверки прав доступа администратора.
    Если пользователь не аутентифицирован или не является администратором,
    возвращает ошибку 403 (Forbidden).
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not is_admin(request.user):
            return HttpResponseForbidden('Доступ только для администратора!')
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    """Отображает главную страницу сайта"""
    return render(request, 'raspisanie/index.html')

def about(request):
    """Отображает страницу 'О колледже'"""
    return render(request, 'raspisanie/about.html')

def contacts(request):
    """Отображает страницу контактов"""
    return render(request, 'raspisanie/contacts.html')

def main(request):
    """Отображает основную страницу расписания"""
    return render(request, 'raspisanie/main.html')

def signup(request):
    """
    Обрабатывает регистрацию новых пользователей.
    При успешной регистрации:
    1. Создает нового пользователя
    2. Хеширует пароль
    3. Создает профиль пользователя с выбранной ролью
    4. Перенаправляет на страницу входа
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user, role=form.cleaned_data['role'])
            messages.success(request, 'Регистрация прошла успешно! Теперь войдите.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'raspisanie/signup.html', {'form': form})

def login_view(request):
    """
    Обрабатывает вход пользователей в систему.
    При успешном входе:
    1. Аутентифицирует пользователя
    2. Создает запись в логе входов
    3. Перенаправляет пользователя в зависимости от его роли:
       - Администратор -> панель администратора
       - Преподаватель -> панель преподавателя
       - Студент -> главная страница
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Логируем вход пользователя
            try:
                LoginLog.objects.create(user=user)
            except Exception:
                pass
            # Перенаправление в зависимости от роли
            if hasattr(user, 'profile'):
                if user.profile.role == 'admin':
                    return redirect('admin_panel_home')
                elif user.profile.role == 'teacher':
                    return redirect('teacher_panel_home')
                else:
                    return redirect('index')
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'raspisanie/login.html', {'form': form})

def logout_view(request):
    """
    Обрабатывает выход пользователя из системы.
    Выполняет разлогинивание и перенаправляет на страницу входа.
    """
    logout(request)
    return redirect('login')

# --- Панель администратора ---
@login_required
def panel_home(request):
    """
    Отображает главную страницу панели администратора.
    Проверяет права доступа и показывает интерфейс управления.
    """
    if not is_admin(request.user):
        return HttpResponseForbidden('Доступ только для администратора!')
    return render(request, 'raspisanie/panel_home.html')

# CRUD операции для групп
@admin_required
def group_list(request):
    """
    Отображает список всех учебных групп.
    Показывает таблицу с названиями групп и количеством студентов.
    """
    groups = Group.objects.all()
    return render(request, 'raspisanie/group_list.html', {'groups': groups})

@admin_required
def group_create(request):
    """
    Создает новую учебную группу.
    Принимает название группы и создает запись в базе данных.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Group.objects.create(name=name)
            return redirect('group_list')
    return render(request, 'raspisanie/group_form.html')

@admin_required
def group_update(request, pk):
    """
    Обновляет информацию о существующей группе.
    Позволяет изменить название группы.
    """
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            group.name = name
            group.save()
            return redirect('group_list')
    return render(request, 'raspisanie/group_form.html', {'group': group})

@admin_required
def group_delete(request, pk):
    """
    Удаляет учебную группу.
    Требует подтверждения перед удалением.
    """
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'raspisanie/group_confirm_delete.html', {'group': group})

@admin_required
def group_students(request, pk):
    """
    Отображает список студентов в конкретной группе.
    Показывает информацию о каждом студенте группы.
    """
    group = get_object_or_404(Group, pk=pk)
    students = group.students.select_related('user').all()
    return render(request, 'raspisanie/group_students.html', {'group': group, 'students': students})

# CRUD операции для преподавателей
@admin_required
def teacher_list(request):
    """
    Отображает список всех преподавателей.
    Показывает информацию о каждом преподавателе.
    """
    teachers = Profile.objects.filter(role='teacher')
    return render(request, 'raspisanie/teacher_list.html', {'teachers': teachers})

@admin_required
def teacher_create(request):
    """
    Создает нового преподавателя.
    Преобразует существующего пользователя в преподавателя.
    """
    if request.method == 'POST':
        user_id = request.POST.get('user')
        if user_id:
            profile = Profile.objects.get(user_id=user_id)
            profile.role = 'teacher'
            profile.save()
            return redirect('teacher_list')
    users = User.objects.exclude(profile__role='teacher')
    return render(request, 'raspisanie/teacher_form.html', {'users': users})

@admin_required
def teacher_update(request, pk):
    """
    Обновляет информацию о преподавателе.
    Позволяет изменить привязку к пользователю.
    """
    teacher = get_object_or_404(Profile, pk=pk, role='teacher')
    if request.method == 'POST':
        user_id = request.POST.get('user')
        if user_id:
            teacher.user_id = user_id
            teacher.save()
            return redirect('teacher_list')
    users = User.objects.all()
    return render(request, 'raspisanie/teacher_form.html', {'teacher': teacher, 'users': users})

@admin_required
def teacher_delete(request, pk):
    """
    Удаляет преподавателя.
    Требует подтверждения перед удалением.
    """
    teacher = get_object_or_404(Profile, pk=pk, role='teacher')
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'raspisanie/teacher_confirm_delete.html', {'teacher': teacher})

# CRUD операции для аудиторий
@admin_required
def room_list(request):
    """
    Отображает список всех аудиторий.
    Показывает номер и вместимость каждой аудитории.
    """
    rooms = Room.objects.all()
    return render(request, 'raspisanie/room_list.html', {'rooms': rooms})

@admin_required
def room_create(request):
    """
    Создает новую аудиторию.
    Принимает номер и вместимость аудитории.
    """
    if request.method == 'POST':
        number = request.POST.get('number')
        if number:
            Room.objects.create(number=number)
            return redirect('room_list')
    return render(request, 'raspisanie/room_form.html')

@admin_required
def room_update(request, pk):
    """
    Обновляет информацию об аудитории.
    Позволяет изменить номер и вместимость.
    """
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        number = request.POST.get('number')
        if number:
            room.number = number
            room.save()
            return redirect('room_list')
    return render(request, 'raspisanie/room_form.html', {'room': room})

@admin_required
def room_delete(request, pk):
    """
    Удаляет аудиторию.
    Требует подтверждения перед удалением.
    """
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('room_list')
    return render(request, 'raspisanie/room_confirm_delete.html', {'room': room})

# CRUD операции для предметов
@admin_required
def subject_list(request):
    """
    Отображает список всех учебных предметов.
    Показывает название предмета и преподавателя.
    """
    subjects = Subject.objects.all()
    return render(request, 'raspisanie/subject_list.html', {'subjects': subjects})

@admin_required
def subject_create(request):
    """
    Создает новый учебный предмет.
    Принимает название предмета и преподавателя.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Subject.objects.create(name=name)
            return redirect('subject_list')
    return render(request, 'raspisanie/subject_form.html')

@admin_required
def subject_update(request, pk):
    """
    Обновляет информацию о предмете.
    Позволяет изменить название и преподавателя.
    """
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            subject.name = name
            subject.save()
            return redirect('subject_list')
    return render(request, 'raspisanie/subject_form.html', {'subject': subject})

@admin_required
def subject_delete(request, pk):
    """
    Удаляет учебный предмет.
    Требует подтверждения перед удалением.
    """
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject_list')
    return render(request, 'raspisanie/subject_confirm_delete.html', {'subject': subject})

# CRUD операции для расписания
@admin_required
def schedule_list(request):
    """
    Отображает список всех занятий в расписании.
    Показывает информацию о группе, предмете, преподавателе, времени и месте.
    """
    schedules = Schedule.objects.select_related('group', 'subject', 'teacher')
    return render(request, 'raspisanie/schedule_list.html', {'schedules': schedules})

@admin_required
def schedule_create(request):
    """
    Создает новое занятие в расписании.
    Принимает информацию о:
    - Группе
    - Предмете
    - Преподавателе
    - Дне недели
    - Времени
    - Дате (опционально)
    """
    groups = Group.objects.all()
    subjects = Subject.objects.all()
    teachers = Profile.objects.filter(role='teacher')
    pair_times = [
        '8:30–9:15', '9:30–10:15', '10:25–11:10', '11:20–12:05', '12:25–13:10', '13:20–14:05', '14:15–15:00'
    ]
    errors = []
    if request.method == 'POST':
        group_id = request.POST.get('group')
        date = request.POST.get('date')
        lessons = []
        for time in pair_times:
            subject_id = request.POST.get(f'subject_{time}')
            teacher_id = request.POST.get(f'teacher_{time}')
            if subject_id and teacher_id:
                lessons.append((time, subject_id, teacher_id))
        if not (group_id and date and lessons):
            errors.append('Все поля обязательны для заполнения!')
        else:
            try:
                group = Group.objects.get(id=group_id)
                date_obj = datetime.strptime(date, "%Y-%m-%d").date()
                for time, subject_id, teacher_id in lessons:
                    Schedule.objects.update_or_create(
                        group=group,
                        date=date_obj,
                        time=time,
                        defaults={
                            'subject_id': subject_id,
                            'teacher_id': teacher_id,
                            'day': ['mon','tue','wed','thu','fri','sat'][date_obj.weekday()]
                        }
                    )
                return redirect('schedule_list')
            except Exception as e:
                errors.append(f'Ошибка при добавлении: {e}')
    return render(request, 'raspisanie/schedule_form.html', {
        'groups': groups, 'subjects': subjects, 'teachers': teachers, 'pair_times': pair_times, 'errors': errors
    })

@admin_required
def schedule_update(request, pk):
    """
    Обновляет информацию о занятии в расписании.
    Позволяет изменить все параметры занятия:
    - Группу
    - Предмет
    - Преподавателя
    - День недели
    - Время
    """
    schedule = get_object_or_404(Schedule, pk=pk)
    groups = Group.objects.all()
    subjects = Subject.objects.all()
    teachers = Profile.objects.filter(role='teacher')
    days = Schedule.DAYS
    if request.method == 'POST':
        group_id = request.POST.get('group')
        subject_id = request.POST.get('subject')
        teacher_id = request.POST.get('teacher')
        day = request.POST.get('day')
        time = request.POST.get('time')
        if group_id and subject_id and teacher_id and day and time:
            schedule.group_id = group_id
            schedule.subject_id = subject_id
            schedule.teacher_id = teacher_id
            schedule.day = day
            schedule.time = time
            schedule.save()
            return redirect('schedule_list')
    return render(request, 'raspisanie/schedule_form.html', {
        'schedule': schedule, 'groups': groups, 'subjects': subjects, 'teachers': teachers, 'days': days
    })

@admin_required
def schedule_delete(request, pk):
    """
    Удаляет занятие из расписания.
    Требует подтверждения перед удалением.
    """
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        return redirect('schedule_list')
    return render(request, 'raspisanie/schedule_confirm_delete.html', {'schedule': schedule})

# --- ADMIN PANEL ---
@login_required
def admin_panel_home(request):
    """
    Главная страница панели администратора.
    Показывает:
    - Статистику системы (количество пользователей, групп, предметов и т.д.)
    - Последние добавленные объекты
    - График посещаемости за последние 14 дней
    """
    if not is_admin(request.user):
        return HttpResponseForbidden('Доступ только для администратора!')

    # Сбор статистики
    users_count = User.objects.count()
    students_count = Profile.objects.filter(role='student').count()
    teachers_count = Profile.objects.filter(role='teacher').count()
    admins_count = Profile.objects.filter(role='admin').count()
    groups_count = Group.objects.count()
    subjects_count = Subject.objects.count()
    schedules_count = Schedule.objects.count()
    today = datetime.now().date()
    schedules_today_count = Schedule.objects.filter(date=today).count()

    # Получение последних добавленных объектов
    last_users = User.objects.order_by('-date_joined')[:5]
    last_groups = Group.objects.order_by('-id')[:5]
    last_schedules = Schedule.objects.select_related('group', 'subject', 'teacher').order_by('-id')[:5]

    # Сбор статистики посещаемости за последние 14 дней
    days = []
    logins = []
    date_from = today - timedelta(days=13)
    login_stats = (
        LoginLog.objects.filter(login_time__date__gte=date_from)
        .annotate(day=TruncDate('login_time'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    login_map = {str(item['day']): item['count'] for item in login_stats}
    for i in range(14):
        d = date_from + timedelta(days=i)
        days.append(d.strftime('%d.%m'))
        logins.append(login_map.get(str(d), 0))

    return render(request, 'raspisanie/admin_panel_home.html', {
        'users_count': users_count,
        'students_count': students_count,
        'teachers_count': teachers_count,
        'admins_count': admins_count,
        'groups_count': groups_count,
        'subjects_count': subjects_count,
        'schedules_count': schedules_count,
        'schedules_today_count': schedules_today_count,
        'last_users': last_users,
        'last_groups': last_groups,
        'last_schedules': last_schedules,
        'days': days,
        'logins': logins,
    })

# --- TEACHER PANEL ---
@login_required
def teacher_panel_home(request):
    """
    Главная страница панели преподавателя.
    Показывает расписание занятий преподавателя на текущий день.
    """
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'teacher':
        return HttpResponseForbidden('Доступ только для преподавателя!')
    schedule = Schedule.objects.select_related('group', 'subject').filter(teacher=request.user.profile).order_by('day', 'time')
    return render(request, 'raspisanie/teacher_panel_home.html', {'schedule': schedule})

# --- CRUD для пользователей (User + Profile) ---
@admin_required
def user_list(request):
    """
    Отображает список всех пользователей системы.
    Показывает основную информацию о каждом пользователе.
    """
    users = User.objects.all().select_related('profile')
    return render(request, 'raspisanie/user_list.html', {'users': users})

@admin_required
def user_create(request):
    """
    Создает нового пользователя.
    Позволяет указать:
    - Имя пользователя
    - Email
    - Пароль
    - Роль (студент/преподаватель/администратор)
    - Группу (для студентов)
    """
    groups = Group.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        group_id = request.POST.get('group')
        if username and password and role:
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )
            profile = Profile.objects.create(user=user, role=role)
            if role == 'student' and group_id:
                profile.group_id = group_id
                profile.save()
            return redirect('user_list')
    return render(request, 'raspisanie/user_form.html', {'groups': groups})

@admin_required
def user_update(request, pk):
    """
    Обновляет информацию о пользователе.
    Позволяет изменить:
    - Имя пользователя
    - Email
    - Пароль
    - Роль
    - Группу (для студентов)
    """
    user = get_object_or_404(User, pk=pk)
    profile = getattr(user, 'profile', None)
    groups = Group.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')
        group_id = request.POST.get('group')
        if username and role:
            user.username = username
            user.email = email
            if password:
                user.password = make_password(password)
            user.save()
            if profile:
                profile.role = role
                if role == 'student':
                    profile.group_id = group_id or None
                else:
                    profile.group = None
                profile.save()
            else:
                profile = Profile.objects.create(user=user, role=role)
                if role == 'student' and group_id:
                    profile.group_id = group_id
                    profile.save()
            return redirect('user_list')
    return render(request, 'raspisanie/user_form.html', {'user_obj': user, 'profile': profile, 'groups': groups})

@admin_required
def user_delete(request, pk):
    """
    Удаляет пользователя из системы.
    Требует подтверждения перед удалением.
    """
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'raspisanie/user_confirm_delete.html', {'user': user})

def schedule_table(request):
    """
    Отображает расписание в виде таблицы.
    Показывает все занятия на неделю для выбранной группы.
    """
    groups = Group.objects.all()
    selected_group = request.GET.get('group')
    schedules = []
    if selected_group:
        schedules = Schedule.objects.filter(
            group_id=selected_group
        ).select_related('subject', 'teacher').order_by('day', 'time')
    return render(request, 'raspisanie/schedule_table.html', {
        'groups': groups,
        'selected_group': selected_group,
        'schedules': schedules
    })

@admin_required
def group_add_students(request, pk):
    """
    Добавляет студентов в группу.
    Позволяет выбрать нескольких студентов из списка доступных.
    """
    group = get_object_or_404(Group, pk=pk)
    available_students = Profile.objects.filter(role='student').exclude(group=group)
    if request.method == 'POST':
        student_ids = request.POST.getlist('students')
        Profile.objects.filter(id__in=student_ids).update(group=group)
        return redirect('group_students', pk=group.pk)
    return render(request, 'raspisanie/group_add_students.html', {'group': group, 'available_students': available_students})

def calendar_view(request):
    """
    Отображает расписание в виде календаря.
    Показывает занятия на месяц с возможностью навигации.
    """
    return render(request, 'raspisanie/calendar.html')

def group_week_schedule(request):
    """
    Отображает расписание группы на неделю.
    Показывает все занятия выбранной группы в течение недели.
    """
    group_name = request.GET.get('group')
    if not group_name:
        return render(request, 'raspisanie/schedule_table_by_group.html', {'error': 'Группа не выбрана'})

    group = get_object_or_404(Group, name=group_name)
    today = datetime.today().date()
    # Начало недели — сегодня, конец — ближайшее воскресенье
    start_date = today
    end_date = today + timedelta(days=(6 - today.weekday()))
    pair_times = [
        '8:30–9:15', '9:30–10:15', '10:25–11:10', '11:20–12:05', '12:25–13:10', '13:20–14:05', '14:15–15:00'
    ]

    # Получаем расписание только с датой в нужном диапазоне
    schedules = Schedule.objects.filter(group=group, date__range=(start_date, end_date))
    # Формируем карту: {date: {time: расписание}}
    schedule_map = {}
    for i in range((end_date - start_date).days + 1):
        d = start_date + timedelta(days=i)
        schedule_map[d] = {}
        for t in pair_times:
            schedule_map[d][t] = ''
    for s in schedules:
        schedule_map[s.date][s.time] = f"{s.subject.name} ({s.teacher.user.get_full_name()})"
    context = {
        'group': group,
        'schedule_map': schedule_map,
        'pair_times': pair_times,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'raspisanie/group_week_schedule.html', context)

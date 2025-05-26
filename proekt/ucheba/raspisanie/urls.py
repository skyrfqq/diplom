from django.urls import path
from . import views

app_name = 'raspisanie'

urlpatterns = [
    # Основные страницы сайта
    path('', views.index, name='index'),  # Главная страница
    path('about/', views.about, name='about'),  # Страница "О колледже"
    path('contacts/', views.contacts, name='contacts'),  # Страница контактов
    path('main/', views.main, name='main'),  # Основная страница расписания

    # Аутентификация
    path('signup/', views.signup, name='signup'),  # Регистрация новых пользователей
    path('login/', views.login_view, name='login'),  # Вход в систему
    path('logout/', views.logout_view, name='logout'),  # Выход из системы

    # Панели управления
    path('panel/', views.panel_home, name='panel_home'),  # Главная страница панели управления
    path('admin/', views.admin_panel_home, name='admin_panel_home'),  # Панель администратора
    path('teacher/', views.teacher_panel_home, name='teacher_panel_home'),  # Панель преподавателя

    # CRUD операции для групп
    path('groups/', views.group_list, name='group_list'),  # Список всех групп
    path('groups/create/', views.group_create, name='group_create'),  # Создание новой группы
    path('groups/<int:pk>/update/', views.group_update, name='group_update'),  # Редактирование группы
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),  # Удаление группы
    path('groups/<int:pk>/students/', views.group_students, name='group_students'),  # Список студентов группы
    path('groups/<int:pk>/add-students/', views.group_add_students, name='group_add_students'),  # Добавление студентов в группу

    # CRUD операции для преподавателей
    path('teachers/', views.teacher_list, name='teacher_list'),  # Список всех преподавателей
    path('teachers/create/', views.teacher_create, name='teacher_create'),  # Создание нового преподавателя
    path('teachers/<int:pk>/update/', views.teacher_update, name='teacher_update'),  # Редактирование преподавателя
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),  # Удаление преподавателя

    # CRUD операции для аудиторий
    path('rooms/', views.room_list, name='room_list'),  # Список всех аудиторий
    path('rooms/create/', views.room_create, name='room_create'),  # Создание новой аудитории
    path('rooms/<int:pk>/update/', views.room_update, name='room_update'),  # Редактирование аудитории
    path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),  # Удаление аудитории

    # CRUD операции для предметов
    path('subjects/', views.subject_list, name='subject_list'),  # Список всех предметов
    path('subjects/create/', views.subject_create, name='subject_create'),  # Создание нового предмета
    path('subjects/<int:pk>/update/', views.subject_update, name='subject_update'),  # Редактирование предмета
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),  # Удаление предмета

    # CRUD операции для расписания
    path('schedule/', views.schedule_list, name='schedule_list'),  # Список всех занятий
    path('schedule/create/', views.schedule_create, name='schedule_create'),  # Создание нового занятия
    path('schedule/<int:pk>/update/', views.schedule_update, name='schedule_update'),  # Редактирование занятия
    path('schedule/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),  # Удаление занятия

    # Управление пользователями
    path('users/', views.user_list, name='user_list'),  # Список всех пользователей
    path('users/create/', views.user_create, name='user_create'),  # Создание нового пользователя
    path('users/<int:pk>/update/', views.user_update, name='user_update'),  # Редактирование пользователя
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),  # Удаление пользователя

    # Просмотр расписания
    path('schedule/table/', views.schedule_table, name='schedule_table'),  # Расписание в виде таблицы
    path('schedule/calendar/', views.calendar_view, name='calendar_view'),  # Расписание в виде календаря
    path('schedule/group-week/', views.group_week_schedule, name='group_week_schedule'),  # Расписание группы на неделю
] 
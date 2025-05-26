@login_required
def admin_panel_home(request):
    if not request.user.is_staff:
        return redirect('home')
    
    # Статистика
    total_users = User.objects.count()
    total_groups = Group.objects.count()
    total_teachers = Teacher.objects.count()
    total_subjects = Subject.objects.count()
    total_schedules = Schedule.objects.count()
    
    # Последние добавленные объекты
    latest_users = User.objects.order_by('-date_joined')[:5]
    latest_groups = Group.objects.order_by('-id')[:5]
    latest_teachers = Teacher.objects.order_by('-id')[:5]
    latest_subjects = Subject.objects.order_by('-id')[:5]
    latest_schedules = Schedule.objects.order_by('-id')[:5]
    
    # Статистика по группам
    groups_stats = Group.objects.annotate(
        student_count=Count('student')
    ).order_by('-student_count')[:5]
    
    # Статистика по преподавателям
    teachers_stats = Teacher.objects.annotate(
        schedule_count=Count('schedule')
    ).order_by('-schedule_count')[:5]
    
    context = {
        'total_users': total_users,
        'total_groups': total_groups,
        'total_teachers': total_teachers,
        'total_subjects': total_subjects,
        'total_schedules': total_schedules,
        'latest_users': latest_users,
        'latest_groups': latest_groups,
        'latest_teachers': latest_teachers,
        'latest_subjects': latest_subjects,
        'latest_schedules': latest_schedules,
        'groups_stats': groups_stats,
        'teachers_stats': teachers_stats,
    }
    return render(request, 'admin_panel_home.html', context) 
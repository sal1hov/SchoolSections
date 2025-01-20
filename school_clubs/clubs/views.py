from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import UserProgress
from .forms import (
    StudentRegistrationForm, ParentRegistrationForm, TeacherRegistrationForm,
    LoginForm, ClubForm, AddStudentToClubForm
)
from .models import Student, Parent, Teacher, Club, Enrollment
import re  # Импортируем модуль для работы с регулярными выражениями
from django.http import JsonResponse

User = get_user_model()

# Главная страница
def home(request):
    return render(request, 'home.html')

# Регистрация ученика
def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = StudentRegistrationForm()
    return render(request, 'register_student.html', {'form': form})

# Регистрация родителя
def register_parent(request):
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ParentRegistrationForm()
    return render(request, 'register_parent.html', {'form': form})

# Регистрация учителя
def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'register_teacher.html', {'form': form})

# Авторизация
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Перенаправление в зависимости от роли
                if user.role == 'student':
                    return redirect('student_dashboard')
                elif user.role == 'parent':
                    return redirect('parent_dashboard')
                elif user.role == 'teacher':
                    return redirect('teacher_dashboard')
                elif user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            else:
                form.add_error(None, "Неверное имя пользователя или пароль")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Выход из системы
def user_logout(request):
    logout(request)
    return redirect('home')

# Личный кабинет ученика
@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('home')

    student = request.user.student
    clubs = Club.objects.all()
    enrolled_club = Enrollment.objects.filter(student=student).first()

    if request.method == 'POST':
        if 'enroll' in request.POST:
            # Проверяем, что ученик еще не записан в кружок
            if not enrolled_club:
                club_id = request.POST.get('club_id')
                club = get_object_or_404(Club, id=club_id)
                if club.available_seats > 0:
                    # Проверяем, что ученик еще не записан в этот кружок
                    if not Enrollment.objects.filter(student=student, club=club).exists():
                        Enrollment.objects.create(student=student, club=club)
                        club.available_seats -= 1
                        club.save()
                        messages.success(request, f"Вы успешно записаны в кружок: {club.name}")
                    else:
                        messages.error(request, "Вы уже записаны в этот кружок.")
                else:
                    messages.error(request, "Мест в кружке больше нет.")
            else:
                messages.error(request, "Вы уже записаны в другой кружок.")
        elif 'cancel' in request.POST:
            enrollment = Enrollment.objects.filter(student=student).first()
            if enrollment:
                club = enrollment.club
                club.available_seats += 1
                club.save()
                enrollment.delete()
                messages.success(request, f"Вы отменили запись в кружок: {club.name}")

        # Перенаправляем на ту же страницу после обработки POST-запроса
        return redirect('student_dashboard')

    return render(request, 'student_dashboard.html', {
        'clubs': clubs,
        'enrolled_club': enrolled_club
    })

# Личный кабинет родителя
@login_required
def parent_dashboard(request):
    if request.user.role != 'parent':
        return redirect('home')

    parent = request.user.parent
    student = Student.objects.filter(user__encrypted_name=parent.student_name).first()

    if request.method == 'POST':
        if student and not student.is_approved_by_parent:
            student.is_approved_by_parent = True
            student.save()
            messages.success(request, "Учащийся утвержден.")
            return redirect('parent_dashboard')

    return render(request, 'parent_dashboard.html', {
        'student': student
    })

# Личный кабинет учителя
@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('home')

    teacher = request.user.teacher
    # Получаем всех учащихся класса учителя, отсортированных по фамилии
    students = Student.objects.filter(grade=teacher.grade).order_by('user__encrypted_name')

    if request.method == 'POST':
        # Обработка подтверждения учащегося
        user_id = request.POST.get('user_id')  # Используем user_id вместо id
        student = get_object_or_404(Student, user_id=user_id)  # Ищем по user_id
        if student.is_approved_by_parent:  # Проверяем, что родитель уже утвердил
            student.is_approved_by_teacher = True
            student.save()
            messages.success(request, f"Учащийся {student.user.encrypted_name} подтвержден.")
            return redirect('teacher_dashboard')

    # Добавляем информацию о кружках для каждого учащегося
    students_with_clubs = []
    for student in students:
        enrollment = Enrollment.objects.filter(student=student).first()
        club_name = enrollment.club.name if enrollment else "Не записан"
        students_with_clubs.append({
            'student': student,
            'club_name': club_name,
        })

    # Получаем список всех доступных кружков
    clubs = Club.objects.all()

    return render(request, 'teacher_dashboard.html', {
        'students_with_clubs': students_with_clubs,
        'clubs': clubs,  # Передаем список кружков в шаблон
    })

# Личный кабинет администратора
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('home')

    # Получаем всех пользователей
    users = User.objects.all()
    clubs = Club.objects.all()

    # Фильтрация по роли
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)

    # Обработка POST-запросов
    if request.method == 'POST':
        # Удаление пользователя
        if 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.delete()
            messages.success(request, f"Пользователь {user.username} удален.")
            return redirect('admin_dashboard')

        # Создание кружка
        if 'create_club' in request.POST:
            club_name = request.POST.get('club_name')
            total_seats = request.POST.get('total_seats')
            Club.objects.create(name=club_name, total_seats=total_seats, available_seats=total_seats)
            messages.success(request, f"Кружок '{club_name}' успешно создан.")
            return redirect('admin_dashboard')

        # Удаление кружка
        if 'delete_club' in request.POST:
            club_id = request.POST.get('club_id')
            club = get_object_or_404(Club, id=club_id)
            club.delete()
            messages.success(request, f"Кружок '{club.name}' удален.")
            return redirect('admin_dashboard')

    return render(request, 'admin_dashboard.html', {
        'users': users,
        'clubs': clubs,
    })

# Смена пароля для ученика
class StudentPasswordChangeView(PasswordChangeView):
    template_name = 'password_change.html'
    success_url = reverse_lazy('student_dashboard')

# Создание кружка (для учителя)
@login_required
def create_club(request):
    if request.user.role != 'teacher':
        return redirect('home')

    if request.method == 'POST':
        form = ClubForm(request.POST)
        if form.is_valid():
            club = form.save(commit=False)
            # Автоматически устанавливаем available_seats равным total_seats
            club.available_seats = club.total_seats
            club.save()
            messages.success(request, "Кружок успешно создан.")
            return redirect('teacher_dashboard')
    else:
        form = ClubForm()

    return render(request, 'create_club.html', {'form': form})

# Добавление ученика в кружок (для учителя)
@login_required
def add_student_to_club(request):
    if request.user.role != 'teacher':
        return redirect('home')

    if request.method == 'POST':
        form = AddStudentToClubForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.save()
            messages.success(request, "Ученик успешно добавлен в кружок.")
            return redirect('teacher_dashboard')
    else:
        form = AddStudentToClubForm()

    return render(request, 'add_student_to_club.html', {'form': form})

# Управление пользователями
@login_required
def manage_users(request):
    if request.user.role != 'admin':
        return redirect('home')

    # Получаем всех пользователей
    users = User.objects.all()

    # Обработка POST-запросов (например, удаление пользователя)
    if request.method == 'POST':
        if 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.delete()
            messages.success(request, f"Пользователь {user.username} удален.")
            return redirect('manage_users')

    return render(request, 'manage_users.html', {
        'users': users
    })

@login_required
def edit_user(request, user_id):
    if request.user.role != 'admin':  # Проверяем, что пользователь — администратор
        return redirect('home')

    user = get_object_or_404(User, id=user_id)  # Получаем пользователя по ID
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.POST.get('username')
        encrypted_name = request.POST.get('encrypted_name')
        role = request.POST.get('role')

        # Проверяем, что ФИО содержит только буквы и пробелы
        if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s]+$', encrypted_name):
            messages.error(request, "ФИО может содержать только буквы и пробелы.")
            return render(request, 'edit_user.html', {'user': user})  # Остаемся на странице редактирования

        # Обновляем данные пользователя
        user.username = username
        user.encrypted_name = encrypted_name
        user.role = role
        user.save()

        # Уведомление об успешном обновлении
        messages.success(request, f"Пользователь {user.username} успешно обновлен.")
        return redirect('admin_dashboard')  # Перенаправляем в личный кабинет администратора

    # Если запрос GET, отображаем форму редактирования
    return render(request, 'edit_user.html', {
        'user': user,  # Передаем объект пользователя в шаблон
    })

@login_required
def edit_club(request, club_id):
    if request.user.role != 'admin':
        return redirect('home')

    club = get_object_or_404(Club, id=club_id)
    if request.method == 'POST':
        # Обработка редактирования кружка
        club.name = request.POST.get('name')
        club.total_seats = request.POST.get('total_seats')
        club.available_seats = request.POST.get('available_seats')
        club.save()
        messages.success(request, f"Кружок '{club.name}' успешно обновлен.")
        return redirect('admin_dashboard')

    return render(request, 'edit_club.html', {
        'club': club,
    })

def tutorial_animation(request):
    return render(request, 'tutorial_animation.html')

@login_required
def save_progress(request):
    if request.method == 'POST':
        step = request.POST.get('step')
        user_progress, created = UserProgress.objects.get_or_create(user=request.user)

        if step == '1':
            user_progress.step_1_completed = True
        elif step == '2':
            user_progress.step_2_completed = True
        elif step == '3':
            user_progress.step_3_completed = True
        elif step == '4':
            user_progress.step_4_completed = True

        user_progress.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_progress(request):
    user_progress, created = UserProgress.objects.get_or_create(user=request.user)
    return JsonResponse({
        'step_1_completed': user_progress.step_1_completed,
        'step_2_completed': user_progress.step_2_completed,
        'step_3_completed': user_progress.step_3_completed,
        'step_4_completed': user_progress.step_4_completed,
    })
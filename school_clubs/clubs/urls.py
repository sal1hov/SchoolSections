from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import tutorial_animation, save_progress, get_progress
from .views import user_login


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/parent/', views.register_parent, name='register_parent'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('parent/', views.parent_dashboard, name='parent_dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),  # Добавлено
    path('edit_club/<int:club_id>/', views.edit_club, name='edit_club'),  # Добавлено

    # URL-адреса для смены пароля
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password_change_done'
    ),

    # Новые URL-адреса для учителя
    path('create_club/', views.create_club, name='create_club'),
    path('add_student_to_club/', views.add_student_to_club, name='add_student_to_club'),
    path('tutorial/', tutorial_animation, name='tutorial_animation'),
    path('save_progress/', save_progress, name='save_progress'),
    path('save_progress/', save_progress, name='save_progress'),
    path('get_progress/', get_progress, name='get_progress'),
    path('login/', user_login, name='login'),
]
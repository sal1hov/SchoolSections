from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Parent, Teacher

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'encrypted_name', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('username', 'email', 'encrypted_name')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        # Сохраняем пользователя
        super().save_model(request, obj, form, change)

        # Автоматически создаем связанные объекты в зависимости от роли
        if obj.role == 'student' and not hasattr(obj, 'student'):
            Student.objects.create(user=obj)
        elif obj.role == 'parent' and not hasattr(obj, 'parent'):
            Parent.objects.create(user=obj)
        elif obj.role == 'teacher' and not hasattr(obj, 'teacher'):
            Teacher.objects.create(user=obj)

# Регистрируем остальные модели
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(Teacher)
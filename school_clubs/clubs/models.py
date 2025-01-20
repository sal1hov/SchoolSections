from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class User(AbstractUser):
    ROLES = (
        ('admin', 'Администратор'),
        ('student', 'Учащийся'),
        ('parent', 'Родитель'),
        ('teacher', 'Классный руководитель'),
    )
    role = models.CharField(max_length=10, choices=ROLES)
    encrypted_name = models.CharField(max_length=255)  # Поле для ФИО
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)  # Новое поле

    # Указываем уникальные имена для обратных ссылок
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="clubs_user_groups",  # Уникальное имя для обратной ссылки
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="clubs_user_permissions",  # Уникальное имя для обратной ссылки
        related_query_name="user",
    )

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для автоматического создания связанных объектов
        (Student, Parent, Teacher) в зависимости от роли пользователя.
        """
        # Сохраняем пользователя
        super().save(*args, **kwargs)

        # Автоматически создаем связанные объекты в зависимости от роли
        if self.role == 'student' and not hasattr(self, 'student'):
            Student.objects.create(user=self)
        elif self.role == 'parent' and not hasattr(self, 'parent'):
            Parent.objects.create(user=self)
        elif self.role == 'teacher' and not hasattr(self, 'teacher'):
            Teacher.objects.create(user=self)

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для автоматического создания связанных объектов
        (Student, Parent, Teacher) в зависимости от роли пользователя.
        """
        # Сохраняем пользователя
        super().save(*args, **kwargs)

        # Автоматически создаем связанные объекты в зависимости от роли
        if self.role == 'student' and not hasattr(self, 'student'):
            Student.objects.create(user=self)
        elif self.role == 'parent' and not hasattr(self, 'parent'):
            Parent.objects.create(user=self)
        elif self.role == 'teacher' and not hasattr(self, 'teacher'):
            Teacher.objects.create(user=self)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    school_ticket_number = models.CharField(max_length=20)
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(11)])
    is_approved_by_parent = models.BooleanField(default=False)  # Добавьте это поле
    is_approved_by_teacher = models.BooleanField(default=False)  # Если нужно, добавьте и это поле

    def __str__(self):
        return self.user.encrypted_name

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_name = models.CharField(max_length=255)

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(11)],
        null=True,  # Разрешаем NULL в базе данных
        blank=True  # Разрешаем пустое значение в форме
    )

class Club(models.Model):
    name = models.CharField(max_length=255)
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

def save(self, commit=True):
    user = super().save(commit=False)
    user.role = 'parent'  # Устанавливаем роль
    if commit:
        user.save()
        # Проверяем, существует ли уже запись для этого пользователя
        parent, created = Parent.objects.get_or_create(
            user=user,
            defaults={'student_name': self.cleaned_data['student_name']}
        )
        if not created:
            # Если запись уже существует, обновляем её
            parent.student_name = self.cleaned_data['student_name']
            parent.save()
    return user

class UserProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    step_1_completed = models.BooleanField(default=False)
    step_2_completed = models.BooleanField(default=False)
    step_3_completed = models.BooleanField(default=False)
    step_4_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Прогресс пользователя {self.user.username}"
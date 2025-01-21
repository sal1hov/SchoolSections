from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Student, Parent, Teacher, Club, Enrollment
import re  # Импортируем модуль для работы с регулярными выражениями

User = get_user_model()

# Кастомный валидатор для ФИО
def validate_name(value):
    """
    Проверяет, что значение содержит только буквы и пробелы.
    """
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s]+$', value):
        raise ValidationError("ФИО может содержать только буквы и пробелы.")

class StudentRegistrationForm(UserCreationForm):
    encrypted_name = forms.CharField(
        max_length=255,
        label="ФИО учащегося",
        validators=[validate_name],
        help_text="Введите ФИО учащегося (только буквы и пробелы)."
    )
    school_ticket_number = forms.CharField(
        max_length=20,
        label="Номер школьного билета",
        help_text="Введите номер школьного билета."
    )
    grade = forms.IntegerField(
        label="Класс",
        validators=[MinValueValidator(1), MaxValueValidator(11)],
        help_text="Введите класс учащегося (от 1 до 11)."
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'encrypted_name', 'school_ticket_number', 'grade']
        labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        help_texts = {
            'username': 'Введите уникальное имя пользователя.',
            'password1': 'Пароль должен содержать не менее 8 символов.',
            'password2': 'Повторите пароль для подтверждения.',
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean_school_ticket_number(self):
        school_ticket_number = self.cleaned_data['school_ticket_number']
        if Student.objects.filter(school_ticket_number=school_ticket_number).exists():
            raise ValidationError("Учащийся с таким номером школьного билета уже зарегистрирован.")
        return school_ticket_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                school_ticket_number=self.cleaned_data['school_ticket_number'],
                grade=self.cleaned_data['grade']
            )
        return user

class ParentRegistrationForm(UserCreationForm):
    encrypted_name = forms.CharField(
        max_length=255,
        label="ФИО родителя",
        validators=[validate_name],
        help_text="Введите ФИО родителя (только буквы и пробелы)."
    )
    student_name = forms.CharField(
        max_length=255,
        label="ФИО учащегося",
        help_text="Введите ФИО учащегося, за которого вы отвечаете."
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'encrypted_name', 'student_name']
        labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        help_texts = {
            'username': 'Введите уникальное имя пользователя.',
            'password1': 'Пароль должен содержать не менее 8 символов.',
            'password2': 'Повторите пароль для подтверждения.',
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'parent'
        if commit:
            user.save()
            Parent.objects.create(
                user=user,
                student_name=self.cleaned_data['student_name']
            )
        return user

class TeacherRegistrationForm(UserCreationForm):
    encrypted_name = forms.CharField(
        max_length=255,
        label="ФИО учителя",
        validators=[validate_name],
        help_text="Введите ФИО учителя (только буквы и пробелы)."
    )
    grade = forms.IntegerField(
        label="Класс",
        validators=[MinValueValidator(1), MaxValueValidator(11)],
        help_text="Введите класс, который вы ведёте (от 1 до 11)."
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'encrypted_name', 'grade']
        labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        help_texts = {
            'username': 'Введите уникальное имя пользователя.',
            'password1': 'Пароль должен содержать не менее 8 символов.',
            'password2': 'Повторите пароль для подтверждения.',
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
            Teacher.objects.create(
                user=user,
                grade=self.cleaned_data['grade']
            )
        return user

# Форма для входа
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

# Форма для создания кружка
class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'total_seats']
        labels = {
            'name': 'Название кружка',
            'total_seats': 'Количество мест',
        }
        help_texts = {
            'name': 'Введите название кружка.',
            'total_seats': 'Введите общее количество мест в кружке.',
        }

# Форма для добавления ученика в кружок
class AddStudentToClubForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'club']
        labels = {
            'student': 'Ученик',
            'club': 'Кружок',
        }
        help_texts = {
            'student': 'Выберите ученика для добавления в кружок.',
            'club': 'Выберите кружок, в который хотите добавить ученика.',
        }
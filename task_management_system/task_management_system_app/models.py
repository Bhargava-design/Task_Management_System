from django.db import models
from django import forms
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)
    is_superuser = forms.BooleanField(
        required=False, label="Register as Superuser"
    )  # Optional field for superuser registration
    is_staff = forms.BooleanField(required=False, label="Staff Member")

    class Meta:
        model = User
        fields = [
            'username',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'email',
            'is_superuser',
            'is_staff',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.is_superuser = self.cleaned_data.get('is_superuser', False)
        user.is_staff = self.cleaned_data.get('is_staff', False)
        if commit:
            user.save()
        return user


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]

    name = models.CharField(max_length=255)  # Increased max_length to accommodate longer task names
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    priority = models.IntegerField(choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(default='', blank=True)  # Allow empty descriptions
    location = models.CharField(max_length=255, default='', blank=True)  # Allow blank values
    organizer = models.CharField(max_length=100, default='', blank=True)  # Allow blank values

    def __str__(self):
        return self.name

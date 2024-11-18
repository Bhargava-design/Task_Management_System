from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Category, Task
from django.shortcuts import render, redirect
from .models import Category
from .models import Task
from django import forms
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required


def is_admin(user):
    return user.is_superuser


admin_required = user_passes_test(lambda user: user.is_superuser)


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('category_list')  # Redirect admin to category list
            else:
                return redirect('user_tasks_list')  # Redirect normal user to tasks list
    else:
        form = AuthenticationForm()
    return render(request, 'task_management_system_app/login.html', {'form': form})


@login_required
def user_tasks_list(request):
    tasks = request.user.tasks.all()
    return render(request, 'task_management_system_app/user_tasks_list.html', {'tasks': tasks})

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
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



class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user with all fields
            login(request, user)  # Log the user in automatically
            if user.is_superuser:  # Redirect superusers to admin page
                return redirect('category_list')  # Admin landing page
            else:
                return redirect('user_tasks_list')  # Normal user landing page
    else:
        form = RegistrationForm()

    return render(request, 'task_management_system_app/register.html', {'form': form})




def LogoutPage(request):
    logout(request)
    return redirect("login")


@login_required
@admin_required
def delete_task(request, task_id):
    if request.method == 'POST':
        task = Task.objects.get(id=task_id)
        task.delete()
    return redirect(reverse('category_list'))


@login_required
@admin_required
def create_task(request):
    if request.method == 'POST':
        # Retrieve data from the POST request
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        priority = request.POST.get('priority')
        description = request.POST.get('description')
        location = request.POST.get('location')
        organizer = request.POST.get('organizer')
        assigned_to_id = request.POST.get('assigned_to')
        category = Category.objects.get(pk=category_id)
        task = Task.objects.create(
            name=name,
            category=category,
            start_date=start_date,
            end_date=end_date,
            priority=priority,
            description=description,
            location=location,
            organizer=organizer,
            assigned_to_id=int(assigned_to_id)
        )

        # Redirect to the task list page
        return redirect('category_list')
    else:
        categories = Category.objects.all()
        users = User.objects.all()
        return render(request, 'task_management_system_app/create_task.html', {'categories': categories, 'users': users})


@login_required
@admin_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    users = User.objects.all()  # Fetch all users for the dropdown

    if request.method == "POST":
        task.name = request.POST.get("name")
        task.start_date = request.POST.get("start_date")
        task.end_date = request.POST.get("end_date")
        task.priority = request.POST.get("priority")
        task.description = request.POST.get("description")
        task.location = request.POST.get("location")
        task.organizer = request.POST.get("organizer")
        task.assigned_to = User.objects.get(id=request.POST.get("assigned_to"))  # Set the assigned user
        
        task.save()
        return redirect("category_list")  # Redirect to task list after update

    return render(request, "task_management_system_app/update_task.html", {"task": task, "users": users})


@login_required
@admin_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'task_management_system_app/category_list.html', {'categories': categories})


@login_required
@admin_required
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Category.objects.create(name=name)
        return redirect('category_list')
    return render(request, 'task_management_system_app/create_category.html')


@login_required
@admin_required
def delete_category(request, category_id):
    category = Category.objects.get(pk=category_id)
    if category.task_set.exists():
        messages.error(
            request, "You cannot delete this category as it contains tasks.")
    else:
        category.delete()
        messages.success(request, "Category deleted successfully.")
    return redirect('category_list')


@login_required
@admin_required
def category_tasks(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    tasks = category.task_set.all()
    return render(request, 'task_management_system_app/category_tasks.html', {'category': category, 'tasks': tasks})


@login_required
@admin_required
def task_chart(request):
    categories = Category.objects.all()
    pending_counts = {}
    
    for category in categories:
        # Modify the query to filter by both category and status
        pending_counts[category.name] = Task.objects.filter(
            category=category,
            priority = 3,  # Assuming status field is used for task status
            start_date__gt=timezone.now()  # If you want only future tasks
        ).count()
    
    return render(request, 'task_management_system_app/task_chart.html', {'pending_counts': pending_counts})
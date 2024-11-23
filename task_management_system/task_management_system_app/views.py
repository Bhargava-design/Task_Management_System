from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Category, Task, RegistrationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Task
from rest_framework import viewsets
from .serializers import CategorySerializer, TaskSerializer
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import UserSerializer


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

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

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
    pending_counts = {
        'Category 1': 10,
        'Category 2': 20,
        'Category 3': 30,
    }
    
    for category in categories:
        # Modify the query to filter by both category and status
        pending_counts[category.name] = Task.objects.filter(
            category=category,
            priority = 3,  # Assuming status field is used for task status
            start_date__gt=timezone.now()  # If you want only future tasks
        ).count()
    
    return render(request, 'task_management_system_app/task_chart.html', {'pending_counts': pending_counts})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
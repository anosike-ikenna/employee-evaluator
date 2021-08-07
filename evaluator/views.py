from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login as DjLogin, logout as DjLogout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import *
from .forms import (
    DepartmentForm, DesignationForm, EvaluatorForm,
    EmployeeForm, TaskForm, ProgressForm,
    EvaluationForm, RatingsForm, AuthenticationForm)
from .utils import perf_averager
from user.forms import UserCreationForm
from datetime import date
from urllib.parse import urlparse
import json
import copy

User = get_user_model()

COLORS = ["bg-red", "bg-teal", "bg-blue", "bg-amber"]

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        form_data = {
            'email': email,
            'password': password
        }
        form = AuthenticationForm(form_data)
        if form.is_valid():
            user = authenticate(email=email, password=password)
            if user:
                DjLogin(request, user)
                return redirect("home")
            else:
                return render(request, "evaluator/login.html", {"form": form, "errors": ["Email/Password is invalid"]})
        else:
            return render(request, "evaluator/login.html", {"form": form})
    return render(request, "evaluator/login.html")

def logout(request):
    DjLogout(request)
    return redirect("login")

def test(request):
    return HttpResponse(f"{request.user.email}")

@login_required
def home(request):
    user = request.user
    context = None
    if not user.is_superuser:
        for group in user.groups.all():
            print(user)
            if group.name == Employee.GROUPS[0]:
                tasks = Task.objects.filter(assigned_to=user.employee).order_by("-created")
                latest_tasks = list(tasks)
                latest_tasks = latest_tasks[:5]
                pending_tasks = tasks.filter(status = "pending")
                inprogress_tasks = tasks.filter(status = "in progress")
                context = {
                    "tasks": tasks,
                    "latest_tasks": latest_tasks,
                    "pending_tasks": pending_tasks,
                    "inprogress_tasks": inprogress_tasks
                }
            elif group.name == Evaluator.GROUPS[0]:
                tasks = Task.objects.filter(evaluator=user.evaluator).order_by("-created")
                latest_tasks = list(tasks)
                latest_tasks = latest_tasks[:5]
                pending_eval = []
                total_eval = []
                completed_tasks = tasks.filter(status = "complete")
                for task in completed_tasks:
                    try:
                        task.evaluation
                    except Task.evaluation.RelatedObjectDoesNotExist:
                        pending_eval.append(task)
                    else:
                        total_eval.append(task)
                context = {
                    "tasks": tasks,
                    "latest_tasks": latest_tasks,
                    "pending_eval": pending_eval,
                    "total_eval": total_eval,
                }
    else:
        departments = Department.objects.count()
        designations = Designation.objects.count()
        users = get_user_model().objects.count()
        employees = Employee.objects.count()
        evaluators = Evaluator.objects.count()
        tasks = Task.objects.all()
        latest_tasks = list(tasks)
        latest_tasks.reverse()
        latest_tasks = latest_tasks[:5]
        context = {
            "departments": departments,
            "designations": designations,
            "users": users,
            "employees": employees,
            "evaluators": evaluators,
            "tasks": tasks,
            "latest_tasks": latest_tasks,
        }
    return render(request, "evaluator/home.html", context)

@login_required
@permission_required("main.view_department", raise_exception=True)
def department_list(request):
    departments = Department.objects.all()
    return render(request, "evaluator/department_list.html", {"departments": departments})

@login_required
@permission_required("main.view_designation", raise_exception=True)
def designation_list(request):
    designations = Designation.objects.all()
    return render(request, "evaluator/designation_list.html", {"designations": designations})

@login_required
@permission_required("main.add_department", raise_exception=True)
def department_new(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            print(request.POST["name"], request.POST["description"])
            form.save()
            messages.add_message(request, messages.SUCCESS, "Department created successfully")
            return redirect("department_list")
        else:
            return render(request, "evaluator/department_new.html", {"form": form})
    return render(request, "evaluator/department_new.html")

@login_required
@permission_required("main.add_designation", raise_exception=True)
def designation_new(request):
    if request.method == "POST":
        form = DesignationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Designation created successfully")
            return redirect("designation_list")
        else:
            return render(request, "evaluator/designation_new.html", {"form": form})
    return render(request, "evaluator/designation_new.html")

@login_required
@permission_required("main.change_department", raise_exception=True)
def department_edit(request, id):
    department = get_object_or_404(Department, id=id)
    context = {"department": department}
    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, f"{department.name.title()} Department updated successfully!")
            return redirect("department_list")
        else:
            context.update({"form": form})
            return render(request, "evaluator/department_edit.html", context)
    department = get_object_or_404(Department, id=id)
    form = DepartmentForm(instance=department)
    context.update({"form": form})
    return render(request, "evaluator/department_edit.html", context)

@login_required
@permission_required("main.change_designation", raise_exception=True)
def designation_edit(request, id):
    designation = get_object_or_404(Designation, id=id)
    context = {"designation": designation}
    if request.method == "POST":
        form = DesignationForm(request.POST, instance=designation)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, f"{designation.name.title()} Designation updated successfully!")
            return redirect("designation_list")
        else:
            context.update({"form": form})
            return render(request, "evaluator/designation_edit.html", context)
    form = DesignationForm(instance=designation)
    context.update({"form": form})
    return render(request, "evaluator/designation_edit.html", context)

@login_required
@permission_required("main.delete_department", raise_exception=True)
def department_delete(request, id):
    department = get_object_or_404(Department, id=id)
    department.delete()
    messages.add_message(request, messages.SUCCESS, f"{department.name.title() } Department deleted successfully!")
    return redirect("department_list")

@login_required
@permission_required("main.delete_designation", raise_exception=True)
def designation_delete(request, id):
    designation = get_object_or_404(Designation, id=id)
    designation.delete()
    messages.add_message(request, messages.SUCCESS, f"{designation.name.title()} Designation deleted successfully!")
    return redirect("designation_list")

@login_required
@permission_required("main.view_evaluator", raise_exception=True)
def evaluator_list(request):
    evaluators = Evaluator.objects.all()
    return render(request, "evaluator/evaluator_list.html", {"evaluators": evaluators})

@login_required
@permission_required("main.add_evaluator", raise_exception=True)
def evaluator_new(request):
    if request.POST:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            avatar = request.FILES.get("avatar")
            evaluator = Evaluator.objects.create(
                avatar=avatar,
                user = user
            )
            user.groups.add(Group.objects.get(name="evaluator"))
            messages.add_message(request, messages.SUCCESS, f"Evaluator with email: {user.email} created successfully")
            return redirect("evaluator_list")
        else:
            return render(request, "evaluator/evaluator_new.html", {"form": form})
    return render(request, "evaluator/evaluator_new.html")

@login_required
@permission_required("main.view_evaluator", raise_exception=True)
def evaluator_detail(request, id):
    evaluator = get_object_or_404(Evaluator, id=id)
    tasks = Task.objects.filter(evaluator=evaluator)
    pending_eval = []
    total_eval = []
    completed_tasks = tasks.filter(status = "complete")
    for task in completed_tasks:
        try:
            task.evaluation
        except Task.evaluation.RelatedObjectDoesNotExist:
            pending_eval.append(task)
        else:
            total_eval.append(task)
    context = {
        "evaluator": evaluator,
        "pending_eval": len(pending_eval),
        "completed_eval": len(total_eval),
    }
    return render(request, "evaluator/evaluator_detail.html", context)

@login_required
@permission_required("main.change_evaluator", raise_exception=True)
def evaluator_edit(request, id):
    evaluator = get_object_or_404(Evaluator, id=id)
    context = {"evaluator": evaluator}
    if request.method == "POST":
        my_dict = {key: request.POST[key] for key in request.POST.keys()}
        user = User.objects.get(email=request.POST["hidden_email"])
        password = user.password
        my_dict.update({"password1": password, "password2": password})
        user_form = UserCreationForm(my_dict, instance=user)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.password = password
            user.save()
            avatar = request.FILES.get("avatar")
            if avatar:
                evaluator.avatar = avatar
                evaluator.user = user
                evaluator.save()
            messages.add_message(request, messages.SUCCESS, f"user with email: {user.email} updated successfully")
            return redirect("evaluator_list")
        else:
            context.update({"form": user_form})
            return render(request, "evaluator/evaluator_edit.html", context)
    form = UserCreationForm(instance=evaluator.user)
    context.update({"form": form})
    return render(request, "evaluator/evaluator_edit.html", context)

@login_required
@permission_required("main.delete_evaluator", raise_exception=True)
def evaluator_delete(request, id):
    evaluator = Evaluator.objects.get(id=id)
    evaluator.user.delete()
    messages.add_message(request, messages.SUCCESS, f"user with email: {evaluator.user.email} delete successfully")
    return redirect("evaluator_list")

@login_required
@permission_required("main.view_employee", raise_exception=True)
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "evaluator/employee_list.html", {"employees": employees})

@login_required
@permission_required("main.add_employee", raise_exception=True)
def employee_new(request):
    designations = Designation.objects.all()
    departments = Department.objects.all()
    context = {"designations": designations, "departments": departments}
    if request.method == "POST":
        user_form = UserCreationForm(request.POST)
        employee_form = EmployeeForm(request.POST, request.FILES)
        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save()
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()
            employee.designations.set(employee_form.cleaned_data["designations"])
            employee.departments.set(employee_form.cleaned_data["departments"])
            user.groups.add(Group.objects.get(name="employee"))
            messages.add_message(request, messages.SUCCESS, f"Employee with email: {user.email} created successfully")
            return redirect("employee_list")
        print(user_form)
        print(employee_form)
        context.update({"employee_form": employee_form, "user_form": user_form})
        return render(request, "evaluator/employee_new.html", context)
    return render(request, "evaluator/employee_new.html", context)

@login_required
@permission_required("main.view_employee", raise_exception=True)
def employee_detail(request, id):
    employee = get_object_or_404(Employee, id=id)
    tasks = Task.objects.filter(assigned_to=employee)
    pending_tasks = tasks.filter(status = "pending")
    inprogress_tasks = tasks.filter(status = "in progress")
    context = {"employee": employee, "colors": COLORS}
    context.update({
        "pending_tasks": pending_tasks.count(),
        "inprogress_tasks": inprogress_tasks.count(),
        "completed_tasks": tasks.count() - pending_tasks.count() - inprogress_tasks.count()
    })
    return render(request, "evaluator/employee_detail.html", context)

@login_required
@permission_required("main.change_employee", raise_exception=True)
def employee_edit(request, id):
    employee = get_object_or_404(Employee, id=id)
    designations = Designation.objects.all()
    departments = Department.objects.all()
    context = {"employee": employee, "designations": designations, "departments": departments}
    if request.method == "POST":
        user = employee.user
        my_dict = {key: request.POST[key] for key in request.POST.keys()}
        password = user.password
        my_dict.update({"password1": password, "password2": password})
        form = UserCreationForm(my_dict, instance=user)
        employee_form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid() and employee_form.is_valid():
            user = form.save(commit=False)
            user.password = password
            user.save()
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()
            employee.departments.set(employee_form.cleaned_data["departments"])
            employee.designations.set(employee_form.cleaned_data["designations"])
            messages.add_message(request, messages.SUCCESS, f"Employee with email: {user.email} updated successfully")
            return redirect("employee_list")
        else:
            print(form, "\n************", employee_form)
            context.update({"form": form, "employee_form": employee_form})
            return render(request, "evaluator/employee_edit.html", context)
    form = UserCreationForm(instance=employee.user)
    employee_form = EmployeeForm(instance=employee)
    print(employee_form)
    context.update({"form": form, "employee_form": employee_form})
    return render(request, "evaluator/employee_edit.html", context)

@login_required
@permission_required("main.employee_delete", raise_exception=True)
def employee_delete(request, id):
    employee = get_object_or_404(Employee, id=id)
    employee.user.delete()
    messages.add_message(request, messages.SUCCESS, f"Employee with email: {employee.user.email} deleted successfully")
    return redirect("employee_list")

@login_required
@permission_required("evaluator.view_task", raise_exception=True)
def task_list(request):
    user = request.user
    context = {}
    if not user.is_superuser:
        for group in user.groups.all():
            if group.name == Employee.GROUPS[0]:
                context.update({
                    "tasks": Task.objects.filter(assigned_to=user.employee)
                })
            elif group.name == Evaluator.GROUPS[0]:
                context.update({
                    "tasks": Task.objects.filter(evaluator=user.evaluator)
                })
    else:
        tasks = Task.objects.all()
        context.update({"tasks": tasks})
    COLORS = {
        "pending": "bg-cyan",
        "in progress": "bg-orange",
        "complete": "bg-red",
    }
    context.update({"date": date.today()})
    return render(request, "evaluator/task_list.html", context)

@login_required
@permission_required("evaluator.add_task", raise_exception=True)
def task_new(request):
    print(f"request path: {request.path}\nrequest full path: {request.get_full_path()}\nuser: {request.user}")
    print(urlparse(request.get_full_path()).query.split("="))
    evaluators = Evaluator.objects.all()
    employees = Employee.objects.all()
    context = {"evaluators": evaluators, "employees": employees}
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.add_message(request, messages.SUCCESS, f"\"{task.name.title()}\" task created successfully")
            return redirect("task_list")
        context.update({"form": form})
        return render(request, "evaluator/task_new.html", context)
    return render(request, "evaluator/task_new.html", context)

@login_required
@permission_required("evaluator.change_task", raise_exception=True)
def task_edit(request, id):
    task = get_object_or_404(Task, id=id)
    evaluators = Evaluator.objects.all()
    employees = Employee.objects.all()
    context = {"evaluators": evaluators, "employees": employees, "task": task}
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, f"\"{task.name.title()}\" task updated successfully")
            return redirect("task_list")
        context.update({'form': form})
        return render(request, "evaluator/task_edit.html", context)
    form = TaskForm(instance=task)
    context.update({"form": form})
    return render(request, "evaluator/task_edit.html", context)

@login_required
@permission_required("evaluator.delete_task", raise_exception=True)
def task_delete(request, id):
    task = get_object_or_404(Task, id=id)
    task.delete()
    messages.add_message(request, messages.SUCCESS, f"\"{task.name.title()}\" task deleted successfully")
    return redirect("task_list")

@login_required
@permission_required("evaluator.add_progress", raise_exception=True)
def progress_new(request, id):
    task = get_object_or_404(Task, id=id)
    if task.status == "complete":
        return HttpResponse("Cannot add anymore progress to this task")
    if request.method == "POST":
        form = ProgressForm(request.POST)
        if form.is_valid():
            progress = form.save(commit=False)
            if request.POST.get("complete"):
                task.status = "complete"
                task.save()
            else:
                task.status = "in progress"
                task.save()
            progress.task = task
            progress.save()
            messages.add_message(request, messages.SUCCESS, "Progress added successfully")
            return redirect("task_list")
        return render(request, "evaluator/progress_new.html")

    form = ProgressForm()
    return render(request, "evaluator/progress_new.html")

@login_required
@permission_required("evaluator.view_progress", raise_exception=True)
def progress_detail(request, id):
    task = get_object_or_404(Task, id=id)
    progresses = list(task.progresses.all().order_by("-id"))
    progresses_dict = [
        {
            "description": progress.description,
            "date_added": progress.date_added.strftime("%d/%m/%Y")
        }
        for progress in progresses
    ]
    complete_res = {
        "complete": True if task.status == "complete" else False,
        "progresses": progresses_dict
    }
    return HttpResponse(
        json.dumps(complete_res),
        content_type="application/json"
    )

@login_required
@permission_required("evaluator.view_evaluation", raise_exception=True)
def evaluation_list(request):
    evaluations = Evaluation.objects.all()
    return render(request, "evaluator/evaluation_list.html", {"evaluations": evaluations})

@login_required
@permission_required("evaluator.add_evaluation", raise_exception=True)
def evaluation_new(request, id):
    task = get_object_or_404(Task, id=id)
    if task.status != "complete":
        error_msg = "You can only evaluate this task once it has been completed!"
        url = reverse("evaluation_list")
        context = {"error_msg": error_msg, "url": url}
        return render(request, "evaluator/error.html", context)
    context = {"task": task, "count": range(1, 6)}
    if request.method == "POST":
        rating_form = RatingsForm(request.POST)
        form = EvaluationForm(request.POST)
        if rating_form.is_valid() and form.is_valid():
            ratings = rating_form.save(commit=False)
            perf_avg = perf_averager(rating_form)
            ratings.performance_average = perf_avg
            ratings.save()
            evaluation = form.save(commit=False)
            evaluation.task = task
            evaluation.ratings = ratings
            evaluation.save()
            messages.add_message(request, messages.SUCCESS, "Evaluation edited successfully")
            return redirect("evaluation_list")
        context.update({"form": form, "rating_form": rating_form})
        return render(request, "evaluator/evaluation_new.html", context)
    return render(request, "evaluator/evaluation_new.html", context)

@login_required
@permission_required("evaluator.change_evaluation", raise_exception=True)
def evaluation_edit(request, id):
    task = get_object_or_404(Task, id=id)
    evaluation = task.evaluation
    ratings = evaluation.ratings
    context = {"evaluation": evaluation, "count": range(1, 6)}
    if request.method == "POST":
        rating_form = RatingsForm(request.POST, instance=ratings)
        form = EvaluationForm(request.POST, instance=evaluation)
        if rating_form.is_valid() and form.is_valid():
            ratings = rating_form.save(commit=False)
            perf_avg = perf_averager(rating_form)
            ratings.performance_average = perf_avg
            ratings.save()
            evaluation = form.save(commit=False)
            evaluation.task = task
            evaluation.ratings = ratings
            evaluation.save()
            messages.add_message(request, messages.SUCCESS, "Evaluation edited successfully")
            return redirect("evaluation_list")
        context.update({"form": form, "rating_form": rating_form})
        return render(request, "evaluator/evaluation_edit.html", context)
    form = EvaluationForm(instance=evaluation)
    rating_form = RatingsForm(instance=ratings)
    print(rating_form)
    context.update({"form": form, "rating_form": rating_form})
    return render(request, "evaluator/evaluation_edit.html", context)

@login_required
@permission_required("evaluator.delete_evaluation", raise_exception=True)
def evaluation_delete(request, id):
    task = get_object_or_404(Task, id=id)
    task.evaluation.delete()
    messages.add_message(request, messages.SUCCESS, "Evaluation deleted successfully")
    return redirect("evaluation_list")
from django.urls import re_path
from . import views

app_name = "api"

urlpatterns = [
    re_path(
        r"^departments/$", 
        views.department_list, 
        name="department_list"),
    re_path(
        r"^departments/(?P<id>\d+)/$", 
        views.department_detail, 
        name="department_detail"),
    re_path(
        r"^designations/$", 
        views.designation_list, 
        name="designation_list"),
    re_path(
        r"^designations/(?P<id>\d+)/$", 
        views.designation_detail, 
        name="designation_detail"),
    re_path(
        r"^evaluators/$", 
        views.evaluator_list, 
        name="evaluator_list"),
    re_path(
        r"^evaluators/(?P<id>\d+)/$", 
        views.evaluator_detail, 
        name="evaluator_detail"),
    re_path(
        r"^employees/$", 
        views.EmployeeListCreate.as_view(), 
        name="employee_list"),
    re_path(
        r"^employees/(?P<id>\d+)/$", 
        views.EmployeeRetrieveUpdateDestroy.as_view(), 
        name="employee_detail"),
    re_path(
        r"^tasks/$", 
        views.TaskListCreate.as_view(), 
        name="task_list"),
    re_path(
        r"^tasks/(?P<id>\d+)/$", 
        views.TaskRetrieveUpdateDestroy.as_view(), 
        name="task_detail"),
    re_path(
        r"^task/(?P<task_id>\d+)/progress/$", 
        views.ProgressListCreate.as_view(), 
        name="progress_list"),
    re_path(
        r"^task/(?P<task_id>\d+)/progress/(?P<progress_id>\d+)/$", 
        views.ProgressRetrieveUpdate.as_view(), 
        name="progress_detail"),
    re_path(
        r"^task/(?P<task_id>\d+)/evaluation/$", 
        views.EvaluationListCreate.as_view(), 
        name="evaluation_list"),
    re_path(
        r"^task/(?P<task_id>\d+)/evaluation/(?P<evaluation_id>\d+)/$", 
        views.EvaluationRetrieveUpdateDestroy.as_view(), 
        name="evaluation_detail"),
    re_path(
        r"^$", 
        views.ApiRoot.as_view(), 
        name="api_root"),
]
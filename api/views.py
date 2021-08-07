from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models.query import QuerySet
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, FormParser
from rest_framework import status
from rest_framework.decorators import (
    api_view, permission_classes, authentication_classes)
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, DjangoModelPermissions,
    DjangoModelPermissionsOrAnonReadOnly)
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.reverse import reverse
from rest_framework.settings import api_settings
from rest_framework.exceptions import (
    ValidationError, PermissionDenied, APIException)
from rest_framework import status
from evaluator.models import *
from .serializers import *
from . import utils
import copy


ERROR_MSG = {
    'does_not_exist': 'Invalid "{obj}" id "{obj_value}" - object does not exist.'
}


@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def department_list(request):
    if request.method == "GET":
        departments = Department.objects.order_by("name")
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS()
        page = pagination_class.paginate_queryset(departments, request)
        if page is not None:
            departments_serializer = DepartmentSerializer(page, many=True)
            return pagination_class.get_paginated_response(departments_serializer.data)
        departments_serializer = DepartmentSerializer(departments, many=True)
        return Response(departments_serializer.data)
    elif request.method == "POST":
        model_meta = Department._meta
        utils.has_django_model_perm(request.user, Department, "add")
        department_serializer = DepartmentSerializer(data=request.data)
        if department_serializer.is_valid():
            department_serializer.save()
            return Response(department_serializer.data, status=status.HTTP_201_CREATED)
        return Response(department_serializer.errors, status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def department_detail(request, id):
    try:
        department = Department.objects.get(id=id)
    except Department.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    model_meta = Department._meta
    if request.method == "GET":
        departments_serializer = DepartmentSerializer(department)
        return Response(departments_serializer.data)
    elif request.method == "PUT":
        utils.has_django_model_perm(request.user, Department, "change")
        department_serializer = DepartmentSerializer(department, request.data)
        if department_serializer.is_valid():
            department_serializer.save()
            return Response(department_serializer.data)
        return Response(department_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PATCH":
        utils.has_django_model_perm(request.user, Department, "change")
        department_serializer = DepartmentSerializer(department, request.data, partial=True)
        if department_serializer.is_valid():
            department_serializer.save()
            return Response(department_serializer.data)
        return Response(department_serializer.errors, status=status.HTTP_404_BAD_REQUEST)
    elif request.method == "DELETE":
        utils.has_django_model_perm(request.user, Department, "delete")
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def designation_list(request):
    if request.method == "GET":
        designations = Designation.objects.all().order_by("name")
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS()
        page = pagination_class.paginate_queryset(designations, request)
        if page is not None:
            designations_serializer = DesignationSerializer(page, many=True)
            return pagination_class.get_paginated_response(designations_serializer.data)
        designations_serializer = DesignationSerializer(designations, many=True)
        return Response(designations_serializer.data)
    elif request.method == "POST":
        model_meta = Designation._meta
        utils.has_django_model_perm(request.user, Designation, "add")
        designation_serializer = DesignationSerializer(data=request.data)
        if designation_serializer.is_valid():
            designation_serializer.save()
            return Response(designation_serializer.data, status=status.HTTP_201_CREATED)
        return Response(designation_serializer.errors, status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def designation_detail(request, id):
    try:
        designation = Designation.objects.get(id=id)
    except Designation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    model_meta = Designation._meta
    if request.method == "GET":
        designations_serializer = DesignationSerializer(designation)
        return Response(designations_serializer.data)
    elif request.method == "PUT":
        utils.has_django_model_perm(request.user, Designation, "change")
        designation_serializer = DesignationSerializer(designation, request.data)
        if designation_serializer.is_valid():
            designation_serializer.save()
            return Response(designation_serializer.data)
        return Response(designation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PATCH":
        utils.has_django_model_perm(request.user, Designation, "change")
        designation_serializer = DesignationSerializer(designation, request.data, partial=True)
        if designation_serializer.is_valid():
            designation_serializer.save()
            return Response(designation_serializer.data)
        return Response(designation_serializer.errors, status=status.HTTP_404_BAD_REQUEST)
    elif request.method == "DELETE":
        utils.has_django_model_perm(request.user, Designation, "delete")
        designation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def evaluator_list(request):
    if request.method == "GET":
        evaluators = Evaluator.objects.all().order_by("user__last_name")
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS()
        page = pagination_class.paginate_queryset(evaluators, request)
        if page is not None:
            evaluators_serializer = EvaluatorSerializer(
                page, many=True, context={"request": request})
            return pagination_class.get_paginated_response(evaluators_serializer.data)
        evaluators_serializer = EvaluatorSerializer(
            evaluators, many=True, context={"request": request})
        return Response(evaluators_serializer.data)
    elif request.method == "POST":
        utils.has_django_model_perm(request.user, Evaluator, "add")
        user_serializer = UserSerializer(data=request.data)
        evaluator_serializer = EvaluatorSerializer(
            data=request.FILES, context={"request": request})
        if evaluator_serializer.is_valid() and user_serializer.is_valid():
            user = user_serializer.save()
            evaluator_serializer.save(user=user)
            return Response(evaluator_serializer.data, status=status.HTTP_201_CREATED)
        user_serializer.is_valid()      # just as a precaution, so user_serializer.errors works
        error_dict = copy.deepcopy(evaluator_serializer.errors)
        error_dict.update(user_serializer.errors)
        return Response(error_dict, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def evaluator_detail(request, id):
    try:
        evaluator = Evaluator.objects.get(id=id)
    except Evaluator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        evaluator_serializer = EvaluatorSerializer(evaluator, context={"request": request})
        return Response(evaluator_serializer.data)
    elif request.method == "PUT":
        utils.has_django_model_perm(request.user, Evaluator, "change")
        user_serializer = UserSerializer(evaluator.user, request.data)
        evaluator_serializer = EvaluatorSerializer(
            evaluator, request.FILES, context={"request": request})
        if evaluator_serializer.is_valid() and user_serializer.is_valid():
            user_serializer.save()
            evaluator_serializer.save()
            return Response(evaluator_serializer.data)
        user_serializer.is_valid()      # just as a precaution, so user_serializer.errors works
        error_dict = copy.deepcopy(evaluator_serializer.errors)
        error_dict.update(user_serializer.errors)
        return Response(error_dict, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PATCH":
        utils.has_django_model_perm(request.user, Evaluator, "change")
        user_serializer = UserSerializer(evaluator.user, request.data, partial=True)
        evaluator_serializer = EvaluatorSerializer(
            evaluator, request.FILES, partial=True, context={"request": request})
        if evaluator_serializer.is_valid() and user_serializer.is_valid():
            user_serializer.save()
            evaluator_serializer.save()
            return Response(evaluator_serializer.data)
        user_serializer.is_valid()
        error_dict = copy.deepcopy(evaluator_serializer.errors)
        error_dict.update(user_serializer.errors)
        return Response(error_dict, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        utils.has_django_model_perm(request.user, Evaluator, "delete")
        user = evaluator.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeListCreate(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, DjangoModelPermissionsOrAnonReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user_serializer = UserSerializer(data=request.data)
        serializer.is_valid()
        user_serializer.is_valid()
        if user_serializer.errors or serializer.errors:
            full_errors = copy.deepcopy(user_serializer.errors)
            full_errors.update(serializer.errors)
            raise ValidationError(full_errors)
        self.perform_create(serializer, user_serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, user_serializer):
        user = user_serializer.save()
        serializer.save(user=user)


class EmployeeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "id"
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, DjangoModelPermissionsOrAnonReadOnly]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user_instance = instance.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        user_serializer = UserSerializer(user_instance, data=request.data, partial=partial)
        serializer.is_valid()
        user_serializer.is_valid()
        if user_serializer.errors or serializer.errors:
            full_errors = copy.deepcopy(user_serializer.errors)
            full_errors.update(serializer.errors)
            raise ValidationError(full_errors)
        self.perform_update(serializer, user_serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer, user_serializer):
        user = user_serializer.save()
        serializer.save(user=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_instance = instance.user
        self.perform_destroy(user_instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, user_instance):
        user_instance.delete()


class TaskListCreate(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, utils.CustomDjangoModelPermissions]

    def get_queryset(self):
        queryset = Task.objects.all()
        user = self.request.user
        if user.is_superuser:
            return queryset
        for group in user.groups.all():
            if group.name == "employee":
                return queryset.filter(assigned_to=user.employee)
            elif group.name == "evaluator":
                return queryset.filter(evaluator=user.evaluator)
        return queryset.none()


class TaskRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "id"
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [
        IsAuthenticated, utils.CustomDjangoModelPermissions, utils.IsTaskOwner
    ]


class ProgressListCreate(generics.ListCreateAPIView):
    permissions_passed = False
    serializer_class = ProgressSerializer
    permission_classes = [
        IsAuthenticated, utils.CustomDjangoModelPermissions, utils.IsTaskOwner
    ]

    def get(self, request, *args, **kwargs):
        self.permissions_passed = True
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permissions_passed = True
        request_task_id = request.data.get("task", None)
        url_task_id = self.kwargs.get("task_id", None)
        assert url_task_id is not None, "Missing `task_id` url kwarg`"
        if request_task_id is not None:
            if request_task_id != url_task_id:
                raise utils.CustomNotAllowedError(
                    detail="Conflicting `task` id in url and in the submitted data"
                )
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        task_id = self.kwargs.get("task_id")
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(self.request, task)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, task)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, task):
        serializer.save(task=task)

    def get_queryset(self):
        task_id = self.kwargs.get("task_id", None)
        assert task_id is not None, "Missing `task_id` url kwarg`"
        if not self.permissions_passed:
            return Progress.objects.all().none()
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(self.request, task)
        return task.progresses.all().order_by("date_added")


class ProgressRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = [
        IsAuthenticated, DjangoModelPermissions, utils.IsTaskOwner
    ]

    def get_object(self):
        task_id = self.kwargs.get("task_id", None)
        progress_id = self.kwargs.get("progress_id", None)
        assert (task_id is not None) and (progress_id is not None), (
            "Missing one or both of `task_id` and `progress_id` url kwargs"
        )
        task = get_object_or_404(Task, id=task_id)
        progress = get_object_or_404(task.progresses, id=progress_id)
        print("here")
        print(task)
        self.check_object_permissions(self.request, task)
        print("nada")
        return progress


class EvaluationListCreate(generics.ListCreateAPIView):
    permissions_passed = False
    serializer_class = EvaluationSerializer
    permission_classes = [
        IsAuthenticated, utils.CustomDjangoModelPermissions, utils.IsTaskOwner
    ]

    def get(self, request, *args, **kwargs):
        self.permissions_passed = True
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permissions_passed = True
        request_task_id = request.data.get("task", None)
        url_task_id = self.kwargs.get("task_id", None)
        assert url_task_id is not None, "Missing `task_id` url kwarg`"
        if request_task_id is not None:
            if request_task_id != url_task_id:
                raise utils.CustomNotAllowedError(
                    detail="Conflicting `task` id in url and in the submitted data"
                )
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        task_id = self.kwargs.get("task_id")
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(self.request, task)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, task)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, task):
        serializer.save(task=task)

    def get_queryset(self):
        task_id = self.kwargs.get("task_id", None)
        assert task_id is not None, "Missing `task_id` url kwarg`"
        if not self.permissions_passed:
            return Evaluation.objects.all().none()
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise utils.CustomNotAllowedError(
                detail=ERROR_MSG["does_not_exist"].format(
                    obj="task",
                    obj_value=task_id),
                code="Invalid")
        has_task_perm = utils.IsTaskOwner().has_object_permission(self.request, self, task)
        if not has_task_perm:
            raise PermissionDenied(detail=None, code=None)
        try:
            evaluation = task.evaluation
        except Task.evaluation.RelatedObjectDoesNotExist:
            raise utils.CustomNotAllowedError(
                detail="This task has not been evaluated yet",
                code="invalid")
        return Evaluation.objects.filter(id=evaluation.id)


class EvaluationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [
        IsAuthenticated, utils.CustomDjangoModelPermissions, utils.IsTaskOwner
    ]

    def get_object(self):
        task_id = self.kwargs.get("task_id", None)
        evaluation_id = self.kwargs.get("evaluation_id", None)
        assert (task_id is not None) and (evaluation_id is not None), (
            "Missing one or both of `task_id` and `evaluator_id` url kwargs"
        )
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(self.request, task)
        try:
            evaluation = task.evaluation
        except Task.evaluation.RelatedObjectDoesNotExist:
            raise utils.CustomNotAllowedError(
                detail="This task has not been evaluated yet",
                code="Invalid")
        if int(evaluation_id) != int(evaluation.id):
            raise utils.CustomNotAllowedError(
                detail=ERROR_MSG["does_not_exist"].format(
                    obj="evaluation",
                    obj_value=evaluation_id),
                code="Invalid")
        return evaluation


class ApiRoot(generics.GenericAPIView):
    
    def get(self, request, *arg, **kwargs):
        return Response({
            "departments": reverse("api:department_list", request=request),
            "designations": reverse("api:designation_list", request=request),
            "evaluator": reverse("api:evaluator_list", request=request),
            "employee": reverse("api:employee_list", request=request),
            "task": reverse("api:task_list", request=request),
        })
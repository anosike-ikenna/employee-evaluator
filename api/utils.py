from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, DjangoModelPermissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import APIException
from rest_framework import status
from evaluator.models import Evaluator, Employee


class StandardResultsPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100


class IsTaskOwner(BasePermission):
    supported_models = ["task", "evaluation", "progress"]
    def has_object_permission(self, request, view, obj):
        model_name = obj._meta.model_name
        assert model_name in self.supported_models, (
            f"`{model_name}` instances are not supported by this permission class."
        )
        user = request.user
        if user.is_superuser:
            return True
        user_groups_names_list = [group.name for group in user.groups.all()]
        if Evaluator.GROUPS[0] in user_groups_names_list:
            if model_name == "task":
                if obj.evaluator.user == user:
                    return True
            elif model_name == "evaluation" or model_name == "progress":
                if obj.task.evaluator.user == user:
                    return True
            return False
        elif Employee.GROUPS[0] in user_groups_names_list:
            if model_name == "task":
                if obj.assigned_to.user == user:
                    return True
            elif model_name == "evaluation" or model_name == "progress":
                if obj.task.assigned_to.user == user:
                    return True
        return False


class CustomDjangoModelPermissions(DjangoModelPermissions):

    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class CustomNotAllowedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


def has_django_model_perm(user, model, perm):
    model_meta = model._meta
    if not user.has_perm(f"{model_meta.app_label}.{perm}_{model_meta.model_name}"):
        raise PermissionDenied(detail=None, code=None)

def perf_averager(ratings):
    efficiency = ratings.get("efficiency")
    timeliness = ratings.get("timeliness")
    quality = ratings.get("quality")
    accuracy = ratings.get("accuracy")
    ratings.update({"performance_average": (efficiency + timeliness + quality + accuracy) * 5})
    return ratings
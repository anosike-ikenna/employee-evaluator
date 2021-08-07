from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import APIException
from rest_framework.reverse import reverse
from evaluator.models import *
from .utils import perf_averager

__all__ = [
    "DepartmentSerializer", "DesignationSerializer", "EvaluatorSerializer",
    "EmployeeSerializer", "UserSerializer", "TaskSerializer",
    "ProgressSerializer", "EvaluationSerializer"
]


class DynamicFieldModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which field should be displayed
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super(DynamicFieldModelSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProgressHyperlinkedIdentity(serializers.HyperlinkedIdentityField):
    view_name = "api:progress_detail"

    def __init__(self, **kwargs):
        super().__init__(self.view_name, **kwargs)

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            "task_id": obj.task.id,
            "progress_id": obj.id
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class EvaluationHyperlinkedIdentity(serializers.HyperlinkedIdentityField):
    view_name = "api:evaluation_detail"

    def __init__(self, **kwargs):
        super().__init__(self.view_name, **kwargs)

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            "task_id": obj.task.id,
            "evaluation_id": obj.id
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class DepartmentSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=Department.objects.all())])
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def create(self, validated_data):
        return Department.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class DesignationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Designation
        fields = "__all__"


class UserSerializer(DynamicFieldModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "phone_number",
            "password"
        )

    def create(self, validated_data):
        print("yes")
        password = validated_data.pop("password")
        user = get_user_model().objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.middle_name = validated_data.get("middle_name", instance.middle_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)
        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))
        instance.save()
        return instance


class EvaluatorSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Evaluator
        fields = (
            "id",
            "url",
            "user",
            "avatar",
        )
        extra_kwargs = {
            "url": {"view_name": "api:evaluator_detail", "lookup_field": "id"}
        }
    
    def create(self, validated_data):
        evaluator = super().create(validated_data)
        evaluator.user.groups.add(
            *list(map(lambda group: Group.objects.get(name=group), Evaluator.GROUPS)))
        return evaluator


class CustomEvaluatorSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.ReadOnlyField(source="__str__")

    class Meta:
        model = Evaluator
        fields = (
            "url",
            "full_name"
        )
        extra_kwargs = EvaluatorSerializer.Meta.extra_kwargs


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(read_only=True)
    designations = serializers.SlugRelatedField(
        many=True,
        queryset=Designation.objects.all(),
        slug_field="name",
    )
    departments = serializers.SlugRelatedField(
        many=True,
        queryset=Department.objects.all(),
        slug_field="name")

    class Meta:
        model = Employee
        fields = "__all__"
        extra_kwargs = {
            "url": {"view_name": "api:employee_detail", "lookup_field": "id"}
        }

    def create(self, validated_data):
        employee = super().create(validated_data)
        employee.user.groups.add(
            *list(map(lambda group: Group.objects.get(name=group), Employee.GROUPS)))
        return employee

    def update(self, instance, validated_data):
        if self.partial == True:
            instance.avatar = validated_data.get("avatar", instance.avatar)
            instance.cv = validated_data.get("cv", instance.cv)
            instance.github = validated_data.get("github", instance.github)
            instance.designations.add(*validated_data.get("designations", [None]))
            instance.departments.add(*validated_data.get("departments", [None]))
            instance.save()
            return instance
        return super().update(instance, validated_data)


class CustomEmployeeSerializer(serializers.HyperlinkedModelSerializer):
    full_name  = serializers.ReadOnlyField(source="__str__")
    class Meta:
        model = Employee
        fields = (
            "url",
            "full_name"
        )
        extra_kwargs = EmployeeSerializer.Meta.extra_kwargs


class CustomProgressSerializer(serializers.HyperlinkedModelSerializer):
    url = ProgressHyperlinkedIdentity()
    class Meta:
        model = Progress
        fields = (
            "id",
            "url",
            "description",
            "date_added"
        )
        extra_kwargs = {
            "task": {"view_name": "api:task_detail", "lookup_field": "id"},
        }


class TaskSerializer(DynamicFieldModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:task_detail", lookup_field="id")
    assigned_to_details = CustomEmployeeSerializer(read_only=True, source="assigned_to")
    evaluator_details = CustomEvaluatorSerializer(read_only=True, source="evaluator")
    progresses = CustomProgressSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "url",
            "assigned_to",
            "assigned_to_details",
            "evaluator",
            "evaluator_details",
            "status",
            "progresses",
            "due_date",
            "created",
        )

class ProgressSerializer(DynamicFieldModelSerializer):
    url = ProgressHyperlinkedIdentity()
    complete = serializers.BooleanField(write_only=True, required=True)
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=False)
    task_description = TaskSerializer(
        read_only=True, source="task", fields=("url", "name", "description"))

    def create(self, validated_data):
        task = validated_data.get("task", None)
        if not task:
            raise serializers.ValidationError(
                {"task": "This field is required"})
        if task.status == Task.COMPLETE:
            raise serializers.ValidationError(
                {"detail": "This task has been completed (progress cannot be added)"})
        if task.status == Task.PENDING:
            task.status = Task.INPROGRESS
        if validated_data.pop("complete"):
            task.status = Task.COMPLETE
        task.save()
        return Progress.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get("description", instance.description)
        instance.save()
        return instance

    class Meta:
        model = Progress
        fields = (
            "id",
            "description",
            "url",
            "task",
            "task_description",
            "date_added",
            "complete",
        )


class RatingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ratings
        fields = "__all__"


class EvaluationSerializer(serializers.ModelSerializer):
    url = EvaluationHyperlinkedIdentity()
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=False)
    ratings = RatingsSerializer()

    class Meta:
        model = Evaluation
        fields = "__all__"

    def create(self, validated_data):
        ratings_data = validated_data.pop("ratings")
        task = validated_data.get("task")
        if not task:
            raise serializers.ValidationError(
                {"task": "This field is required"})
        try:
            if task.status != Task.COMPLETE:
                raise serializers.ValidationError({
                    "detail": "Target Task has not been completed yet."})
            validated_data.get("task").evaluation
            raise serializers.ValidationError(
                {"detail": "Target Task has already been evaluated"})
        except Task.evaluation.RelatedObjectDoesNotExist:
            ratings_data = perf_averager(ratings_data)
            ratings = Ratings.objects.create(**ratings_data)
            return Evaluation.objects.create(**validated_data, ratings=ratings)
        raise APIException(detail="Something went wrong. Try again")
        

    def update(self, instance, validated_data):
        ratings = instance.ratings
        ratings_data = validated_data.pop("ratings", None)
        if ratings_data:
            ratings.efficiency = ratings_data.setdefault("efficiency", ratings.efficiency)
            ratings.efficiency = ratings_data.setdefault("efficiency", ratings.efficiency)
            ratings.timeliness = ratings_data.setdefault("timeliness", ratings.timeliness)
            ratings.quality = ratings_data.setdefault("quality", ratings.quality)
            ratings.accuracy = ratings_data.setdefault("accuracy", ratings.accuracy)
            ratings.performance_average = perf_averager(ratings_data).get(
                "performance_average")
        ratings.save()
        instance.task = validated_data.get("task", instance.task)
        instance.remarks = validated_data.get("remarks", instance.remarks)
        instance.save()
        return instance
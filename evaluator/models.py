from django.db import models
from django.core.validators import MaxValueValidator
from django.urls import reverse
from django.conf import settings

__all__ = [
    "Designation", "Department", "Evaluator", "Employee",
    "Task", "Progress", "Ratings", "Evaluation",
]

class Designation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)

    def get_edit_url(self):
        return reverse("designation_edit", kwargs={
            "id": self.id
        })

    def get_delete_url(self):
        return reverse("designation_delete", kwargs={
            "id": self.id
        })

    def __str__(self):
        return self.name.title()


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)

    def get_edit_url(self):
        return reverse("department_edit", kwargs={
            "id": self.id
        })

    def get_delete_url(self):
        return reverse("department_delete", kwargs={
            "id": self.id
        })

    def __str__(self):
        return self.name.title()


class Option(models.Model):
    a = models.CharField(max_length=300,)
    b = models.CharField(max_length=300)
    c = models.CharField(max_length=300)
    d = models.CharField(max_length=300)

    def __Str__(self):
        return [
            ("a", self.a),
            ("b", self.b),
            ("c", self.c),
            ("d", self.d),
        ]


class Question(models.Model):
    description = models.TextField()
    options = models.OneToOneField(Option, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1)

    def __str__(self):
        return self.description


class TestResult(models.Model):
    correct = models.PositiveIntegerField(default=0)
    incorrect = models.PositiveIntegerField(default=0)
    score = models.PositiveIntegerField(default=0)


class RegularUser(models.Model):
    avatar = models.ImageField(upload_to="reg_users/", blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} {self.user.middle_name}"


class Evaluator(models.Model):
    GROUPS = ["evaluator"]
    avatar = models.ImageField(upload_to="evaluators/", blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True) 

    def get_absolute_url(self):
        return reverse("evaluator_detail", kwargs={
            "id": self.id
        })

    def get_edit_url(self):
        return reverse("evaluator_edit", kwargs={
            "id": self.id
        })

    def get_delete_url(self):
        return reverse("evaluator_delete", kwargs={
            "id": self.id
        })

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} {self.user.middle_name}"


class Employee(models.Model):
    GROUPS = ["employee"]
    avatar = models.ImageField(upload_to="employee/", blank=True)
    cv = models.FileField(upload_to="cvs", blank=True)
    github = models.URLField(verbose_name="github page", max_length=200, blank=True)
    designations = models.ManyToManyField(Designation, related_name="employees")
    departments = models.ManyToManyField(Department, related_name="employees")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)
    created = models.DateField(verbose_name="date created", auto_now_add=True)

    def get_absolute_url(self):
        return reverse("employee_update", kwargs={
            "id": self.id
        })

    def get_edit_url(self):
        return reverse("employee_edit", kwargs={
            "id": self.id
        })

    def get_delete_url(self):
        return reverse("employee_delete", kwargs={
            "id": self.id
        })

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} {self.user.middle_name}"


class Applicant(models.Model):
    avatar = models.ImageField(upload_to="employee/")
    cv = models.FileField(upload_to="cvs")
    github = models.URLField(verbose_name="github page", max_length=200)
    designation = models.ManyToManyField(Designation, related_name="applicants")
    department = models.ManyToManyField(Department, related_name="applicants")
    status = models.CharField(max_length=30, default="pending")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ManyToManyField(Question, through="QuestionAnswered")
    test_result = models.OneToOneField(
        TestResult, verbose_name="test result", blank=True, on_delete=models.CASCADE)
    created = models.DateField(verbose_name="date created", auto_now_add=True)

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} {self.user.middle_name}"


class QuestionAnswered(models.Model):
    user = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1, blank=True)

    class Meta:
        verbose_name = "Question Answered"
        verbose_name_plural = "Questions Answered"


class Task(models.Model):
    PENDING = "pending"
    INPROGRESS = "in progress"
    COMPLETE = "complete"
    STATUS_CHOICES = [
        (PENDING, PENDING),
        (INPROGRESS, INPROGRESS),
        (COMPLETE, COMPLETE)
    ]
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    assigned_to = models.ForeignKey(
        Employee, verbose_name="assigned to", on_delete=models.CASCADE)
    evaluator = models.ForeignKey(Evaluator, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=PENDING, blank=True)
    due_date = models.DateField("Date Due")
    created = models.DateField(auto_now_add=True)

    class Meta:
        get_latest_by = "created"

    def get_absolute_url(self):
        return reverse("task_detail", kwargs={
            "id": self.id
        })

    def get_edit_url(self):
        return reverse("task_edit", kwargs={
            "id": self.id
        })

    def get_delete_url(self):
        return reverse("task_delete", kwargs={
            "id": self.id
        })

    def __str__(self):
        return self.name.capitalize()


class Progress(models.Model):
    description = models.TextField()
    task = models.ForeignKey(Task, related_name="progresses", on_delete=models.CASCADE)
    date_added = models.DateField("date added", auto_now_add=True)

    def __str__(self):
        return self.description


class Ratings(models.Model):
    efficiency = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    timeliness = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    quality = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    accuracy = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    performance_average = models.PositiveIntegerField(
        blank=True, validators=[MaxValueValidator(100)])

    def __str__(self):
        return f"Efficiency: {self.efficiency}\n"\
               f"Timeliness: {self.timeliness}\n"\
               f"Quality: {self.quality}\n"\
               f"Accuracy: {self.accuracy}\n"\
               f"performance_average: {self.performance_average}"


class Evaluation(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, blank=True)
    date_evaluated = models.DateField(verbose_name="date evaluated", auto_now_add=True)
    remarks = models.TextField(max_length=300)
    ratings = models.OneToOneField(Ratings, on_delete=models.CASCADE, blank=True)

    def get_edit_url(self):
        return reverse("evaluation_edit", kwargs={
            "id": self.task.id
        })

    class Meta:
        ordering = ["-date_evaluated"]
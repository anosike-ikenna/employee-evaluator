from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django import forms
from django.conf import settings
from .models import (
    Designation, Department, Evaluator,
    Employee, Applicant, Task,
    Progress, Evaluation, Ratings)


class AuthenticationForm(forms.Form):
    
    email = forms.EmailField()
    password = forms.CharField(widget = forms.PasswordInput())

    def clean_email(self):
        return self.cleaned_data['email'].lower()


class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Department
        fields = "__all__"

    def clean_name(self):
        return self.cleaned_data['name'].lower()

    def clean_description(self):
        return self.cleaned_data['description'].lower()


class DesignationForm(forms.ModelForm):

    class Meta:
        model = Designation
        fields = "__all__"

    def clean_name(self):
        return self.cleaned_data['name'].lower()
    
    def clean_description(self):
        return self.cleaned_data['description'].lower()


class EvaluatorForm(forms.ModelForm):

    class Meta:
        model = Evaluator
        fields = "__all__"


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = "__all__"

    def clean_github(self):
        return self.cleaned_data["github"].lower()


class ApplicantForm(forms.ModelForm):

    class Meta:
        model = Applicant
        fields = "__all__"
    
    def clean_github(self):
        return self.cleaned_data["github"].lower()


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = "__all__"


class ProgressForm(forms.ModelForm):
    
    complete = forms.BooleanField(required=False)

    class Meta:
        model = Progress
        fields = ["description", "complete"]


class EvaluationForm(forms.ModelForm):

    class Meta:
        model = Evaluation
        fields = "__all__"


class RatingsForm(forms.ModelForm):

    class Meta:
        model = Ratings
        fields = "__all__"
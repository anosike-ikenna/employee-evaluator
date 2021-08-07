from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as MyUserCreationForm
from django.core.exceptions import ValidationError
import re


class UserCreationForm(MyUserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ["first_name", "middle_name", "last_name", "email", "phone_number"]
    
    def clean_phone_number(self):
        regex = re.compile(r"\d{11}")
        phone_number = self.cleaned_data["phone_number"]
        match = regex.match(phone_number)
        if not match:
            raise ValidationError("Enter a valid phone number")
        return phone_number
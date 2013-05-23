from django import forms
from django.contrib.auth.hashers import make_password
from opencollea.models import *


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['date_joined', 'last_login']


class RegistrationDetailsForm(forms.ModelForm):
    first_name = forms.CharField(required=True)   # Override to be required
    last_name = forms.CharField(required=True)    # Override to be required
    email = forms.EmailField(required=True)       # Override to be required
    password = forms.CharField(min_length=6, required=False,
                               widget=forms.PasswordInput)
    password_confirmation = forms.CharField(required=False,
                                            widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_password_confirmation(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_confirmation')

        if password1 and len(password1) > 3:
            if password1 != password2:
                raise forms.ValidationError('Password must match')
            else:
                self.cleaned_data['password'] = \
                    make_password(self.cleaned_data['password'])
        else:
            # Uporabnik ne zeli spremenit gesla
            # To je workaround k se mi ne da vec zajebavat
            user = User.objects.get(pk=self.instance.id)
            self.cleaned_data['password'] = user.password


class EtherpadNoteForm(forms.ModelForm):
    class Meta:
        model = EtherpadNote


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer

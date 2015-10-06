###############################################################################
## the capital letter for all keywords and 'Form is at the end of keywords
##############################################################################

from django import forms
# from django.contrib.auth.models import User
from accounts.models import *
from django.contrib.auth.forms import UserCreationForm

# class for user regitration, create user and save user into database user table, at the same time create user
# profile and active key and expire time, and then save them into userprofile table


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email address'})) # user email address, above fields is set to required to identify
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')  # define form fields

# Clean email field
    def clean_email(self):
        email = self.cleaned_data["email"]  #when pos/get submit, mail address is cleaned firstly and equal to eamil
#         #  variable
        try:
            User._default_manager.get(email=email)  # check mail is unique in database, if ger value, the mail is
#             # registed
        except User.DoesNotExist:  # mail is not registed, error will raised, and then return mail
            return email
        raise forms.ValidationError('duplicate email')  # form validation erros raised

    # modify save() method so that we can set user.is_active to False when we first create our user
    def save(self, commit = True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.is_active = False
            user.save()
        return user

class ResetPasswordForm(forms.Form):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder':'Email address'}))
    password1 = forms.CharField(max_length=32, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=32, widget=forms.PasswordInput)


    def save(self):
        user_email = self.cleaned_data['email']
        user = User.objects.get(email=user_email)
        user.is_active = False
        user.save()

class ProfileForm(forms.ModelForm):
    birthday = forms.DateField()
    class Meta:
        model = UserProfle
        fields = ('website', 'birthday')

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')



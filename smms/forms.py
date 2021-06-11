from django.contrib.auth.models import User
from django import forms

from . import models


class UserUpdateForm(forms.ModelForm):
    """form for update user info"""

    class Meta:
        model = models.Profile
        exclude = ('user',)


class UserForm(forms.ModelForm):
    """form for base user"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)


class ProfileForm(forms.Form):
    """ form for creating new user"""

    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    gender = forms.CharField(max_length=10)
    email = forms.EmailField()
    phone = forms.CharField(max_length=13)
    state = forms.CharField(max_length=10)
    rank = forms.CharField(max_length=20)
    image = forms.ImageField()
    address = forms.CharField(max_length=40, widget=forms.Textarea())


class AddSaleForm(forms.ModelForm):
    class Meta:
        model = models.Sale
        fields = "__all__"


class AddProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = "__all__"


class EditProductForm(forms.ModelForm):
    """form for updating products"""

    class Meta:
        model = models.Product
        fields = "__all__"


class EditSalesForm(forms.ModelForm):
    """for updating sales record"""

    class Meta:
        model = models.Sale
        fields = "__all__"


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = models.Message
        fields = "__all__"

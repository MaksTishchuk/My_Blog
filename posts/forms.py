from django.forms import ModelForm, Form
from django import forms
from django.http import HttpResponse
from .models import *


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'status']


class ProfileForm(ModelForm):
    date_of_birth = forms.DateField(
        required=False,
        label='Дата рождения',
        widget=forms.DateInput(attrs={'placeholder': 'В формате YYYY-MM-DD'})
    )

    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
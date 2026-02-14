from django import forms
import Instagram.models as models
from django.contrib.auth.forms import UserCreationForm

class CustomUserForm(UserCreationForm):
    class Meta:
        model = models.CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

class PostsForm(forms.ModelForm):
    class Meta:
        model = models.Posts
        fields = ("post", "text")

class StoryForm(forms.ModelForm):
    class Meta:
        model = models.Story
        fields = ("story",)

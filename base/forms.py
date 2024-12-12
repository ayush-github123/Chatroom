from django import forms
from .models import Room, blog

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class BlogForm(forms.ModelForm):
    class Meta:
        model=blog
        fields = '__all__'
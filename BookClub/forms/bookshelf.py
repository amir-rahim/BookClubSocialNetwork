from django import forms
from django.forms import Form

class AddBookShelfForm(Form):
    user = forms.IntegerField()
    book = forms.IntegerField()
    status = forms.IntegerField()
    


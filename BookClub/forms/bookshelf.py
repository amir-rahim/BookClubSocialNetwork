from django import forms

from BookClub.models import BookShelf

class AddBookShelfForm(forms.ModelForm):
    class Meta:
        model = BookShelf
        fields = ("book", "user", "status")
        widgets = {
            "book": forms.TextInput(attrs={'type': 'hidden'}),
            "user": forms.TextInput(attrs={'type': 'hidden'}),
            "status": forms.Select(choices=BookShelf.ListType)
        }

    


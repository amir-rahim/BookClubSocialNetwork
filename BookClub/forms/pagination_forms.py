from django import forms


class PaginationByForm(forms.Form):
    numberChoices = [(10, 10), (20, 20), (50, 50), (100, 100)]

    paginate = forms.ChoiceField(choices=numberChoices,
                                 widget=forms.Select(attrs={'onchange': 'form.submit();'}),
                                 label='')

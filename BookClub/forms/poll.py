from datetime import datetime

import pytz
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator

from BookClub.models import Club, Book, Poll, Option


class ISBNField(forms.CharField):
    default_validators = [
        RegexValidator(
            regex=r'^([\d]+)(X)?$',
            message='ISBN value should only consist of 10 or 13 digits with final digit possibly ending in character X'
        )
    ]

    def __init__(self, *args, **kwargs):
        kwargs['min_length'] = 10
        kwargs['max_length'] = 13
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cleaned_field_data = super().clean(*args, **kwargs)

        if not self.required and not cleaned_field_data:
            return cleaned_field_data
        if(len(cleaned_field_data) == 10 or len(cleaned_field_data) == 13) and Book.objects.filter(ISBN=cleaned_field_data).exists():
            return cleaned_field_data
        else:
            raise ValidationError(
                'Invalid value: non-existing ISBN was entered',
                code='invalid'
            )


class PollForm(forms.Form):
    poll_title = forms.CharField(max_length=120)
    deadline = forms.DateTimeField(required=False, label='Voting deadline [YYYY-MM-DD hh:mm:ss]',
                                   widget=forms.TextInput(attrs={'placeholder': 'Optional'}))

    option_1_text = forms.CharField(max_length=120)
    option_1_isbn = ISBNField(required=False, label='Attach book (enter ISBN) to option 1',
                              widget=forms.TextInput(attrs={'placeholder': 'Optional'}))

    option_2_text = forms.CharField(max_length=120)
    option_2_isbn = ISBNField(required=False, label='Attach book (enter ISBN) to option 2',
                              widget=forms.TextInput(attrs={'placeholder': 'Optional'}))

    option_3_text = forms.CharField(max_length=120, required=False,
                                    widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    option_3_isbn = ISBNField(required=False, label='Attach book (enter ISBN) to option 3',
                              widget=forms.TextInput(attrs={'placeholder': 'Optional'}))

    option_4_text = forms.CharField(max_length=120, required=False,
                                    widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    option_4_isbn = ISBNField(required=False, label='Attach book (enter ISBN) to option 4',
                              widget=forms.TextInput(attrs={'placeholder': 'Optional'}))

    option_5_text = forms.CharField(max_length=120, required=False,
                                    widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    option_5_isbn = ISBNField(required=False, label='Attach book (enter ISBN) to option 5',
                              widget=forms.TextInput(attrs={'placeholder': 'Optional'}))

    def save(self, club):
        if not self.is_valid():
            raise ValidationError('Form data invalid, check errors', code='invalid')

        if not isinstance(club, Club) or not club.pk:
            raise ObjectDoesNotExist('Supplied club object for creator is invalid')

        poll_active = True
        if self.cleaned_data['deadline'] and (self.cleaned_data['deadline'] < pytz.utc.localize(datetime.now())):
            poll_active = False

        new_poll = Poll(
            title=self.cleaned_data['poll_title'],
            club=club,
            deadline=self.cleaned_data['deadline'],
            active=poll_active
        )
        new_poll.full_clean()
        new_poll.save()

        saved_options = []

        # Saving required options
        for i in range(1, 3):
            text_key = 'option_' + str(i) + '_text'
            isbn_key = 'option_' + str(i) + '_isbn'
            option_n_input = self.cleaned_data[text_key]
            option_n_isbn_input = self.cleaned_data[isbn_key]
            option_n_book = None
            if option_n_isbn_input:
                option_n_book = Book.objects.get(ISBN=option_n_isbn_input)

            option_n = Option(text=option_n_input, poll=new_poll, book=option_n_book)
            option_n.full_clean()
            option_n.save()

            saved_options.append(option_n)

        # saving optional options
        for i in range(3, 6):
            text_key = 'option_' + str(i) + '_text'
            option_n_input = self.cleaned_data[text_key]

            if option_n_input:
                isbn_key = 'option_' + str(i) + '_isbn'
                option_n_isbn_input = self.cleaned_data[isbn_key]
                option_n_book = None
                if option_n_isbn_input:
                    option_n_book = Book.objects.get(ISBN=option_n_isbn_input)

                option_n = Option(text=option_n_input, poll=new_poll, book=option_n_book)
                option_n.full_clean()
                option_n.save()
                saved_options.append(option_n)

        return new_poll, saved_options

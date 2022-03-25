
from django.forms.widgets import Input
from django.forms import DateInput, DateTimeInput
from django.contrib.contenttypes.models import ContentType

class BookSelectorInput(Input):
    input_type = 'hidden'
    template_name = 'partials/book_search_select.html/'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['content_type'] = ContentType.objects.get(app_label="BookClub", model="book").pk
        return context


class DateTimePickerInput(DateTimeInput):
    input_type = 'datetime'
    

class DatePickerInput(DateInput):
    input_type = 'date'

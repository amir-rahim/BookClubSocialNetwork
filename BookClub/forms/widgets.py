
from django.forms.widgets import Input
from django.forms import DateInput, DateTimeInput

class BookSelectorInput(Input):
    input_type = 'hidden'
    template_name = 'partials/book_search_select.html/'


class DateTimePickerInput(DateTimeInput):
    input_type = 'datetime'
    

class DatePickerInput(DateInput):
    input_type = 'date'

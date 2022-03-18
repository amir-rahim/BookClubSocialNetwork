from django.forms import DateInput, DateTimeInput

class DateTimePickerInput(DateTimeInput):
    input_type = 'datetime'
    

class DatePickerInput(DateInput):
    input_type = 'date'

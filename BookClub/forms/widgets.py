from django.forms.widgets import Input


class BookSelectorInput(Input):
    input_type = 'hidden'
    template_name = 'partials/book_search_select.html/'

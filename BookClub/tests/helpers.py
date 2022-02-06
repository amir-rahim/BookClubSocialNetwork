from django.urls import reverse
from django.utils.http import urlencode

def reverse_with_query(url_name, kwargs = None, query_kwargs = None):
    url = reverse(url_name, kwargs=kwargs)

    if query_kwargs:
        return f'{url}?{urlencode(query_kwargs)}'

    return url

def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url


class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
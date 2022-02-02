from django.urls import reverse

"""Reverse users to next url if exists"""
def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url
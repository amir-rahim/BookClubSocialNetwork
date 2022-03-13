from django.test import TestCase, tag
from django.urls import reverse


@tag("views", "books", "library_dashboard")
class LibraryDashboardViewTestCase(TestCase):
    """Tests of the Library Dashboard view"""

    def setUp(self):
        self.url = reverse('library_dashboard')

    def test_dashboard_url(self):
        self.assertEqual(self.url, '/library/')

    def test_get_dashboard(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library_dashboard.html')

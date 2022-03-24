import random

from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Book, BookReview


@tag("views", "books", "book_detail")
class BookDetailViewTestCase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/real_books.json',
        'BookClub/tests/fixtures/default_users.json',
    ]

    def setUp(self):
        self.book = Book.objects.get(pk=54273)
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.user3 = User.objects.get(pk=3)
        self.user4 = User.objects.get(pk=4)
        self.url = reverse('book_view', kwargs={'book_id': 54273})

    def test_url(self):
        self.assertEquals(self.url, "/library/books/" + str(54273) + "/")

    def test_contains_book_data(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'book_detail_view.html')
        context = response.context
        self.assertEqual(context['book'], self.book)

    def test_redirect_invalid_book(self):
        url = reverse('book_view', kwargs={'book_id' : 99999})
        response = self.client.get(url)
        self.assertTemplateNotUsed(response, 'book_detail_view.html')
        self.assertEqual(response.status_code, 404)

    def test_displays_book_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail_view.html')
        content = response.content
        self.assertContains(response, 'Author')
        self.assertContains(response, self.book.ISBN)
        # this next test uses a specific value rather than accessing book.title
        # this is because the webpage formats the punctuation in the title differently
        # and I felt this was more suitable than spending time trying to convert.
        self.assertContains(response, "Arthur&#x27;s Tooth (Arthur Adventure Series)")
        self.assertContains(response, self.book.getPublicationYear())
        self.assertContains(response, self.book.publisher)
        self.assertContains(response, self.book.imageL)

    def test_displays_no_review_message(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail_view.html')
        content = response.content
        self.assertContains(response, 'Author')
        self.assertContains(response, self.book.ISBN)
        # this next test uses a specific value rather than accessing book.title
        # this is because the webpage formats the punctuation in the title differently
        # and I felt this was more suitable than spending time trying to convert.
        self.assertContains(response, "Arthur&#x27;s Tooth (Arthur Adventure Series)")
        self.assertContains(response, self.book.getPublicationYear())
        self.assertContains(response, self.book.publisher)
        self.assertContains(response, self.book.imageL)
        self.assertContains(response, "No reviews as of yet")

    def test_displays_1_review_message(self):
        review = BookReview.objects.create(
            creator=self.user1,
            book=self.book,
            title="I literally picked a random number",
            book_rating=random.randrange(0, 10),
            content="Material Gworl1"
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail_view.html')
        content = response.content
        self.assertContains(response, 'Author')
        self.assertContains(response, self.book.ISBN)
        # this next test uses a specific value rather than accessing book.title
        # this is because the webpage formats the punctuation in the title differently
        # and I felt this was more suitable than spending time trying to convert.
        self.assertContains(response, "Arthur&#x27;s Tooth (Arthur Adventure Series)")
        self.assertContains(response, self.book.getPublicationYear())
        self.assertContains(response, self.book.publisher)
        self.assertContains(response, self.book.imageL)
        self.assertContains(response, 'Material Gworl1')

    def test_displays_2_review_message(self):
        review = BookReview.objects.create(
            creator=self.user1,
            book=self.book,
            title="Random rating Uno",
            book_rating=random.randrange(0, 10),
            content="Material Gworl1"
        )
        review = BookReview.objects.create(
            creator=self.user2,
            book=self.book,
            title="Random rating Dos",
            book_rating=random.randrange(0, 10),
            content="Material Gworl2"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail_view.html')
        content = response.content
        self.assertContains(response, 'Author')
        self.assertContains(response, self.book.ISBN)
        # this next test uses a specific value rather than accessing book.title
        # this is because the webpage formats the punctuation in the title differently
        # and I felt this was more suitable than spending time trying to convert.
        self.assertContains(response, "Arthur&#x27;s Tooth (Arthur Adventure Series)")
        self.assertContains(response, self.book.getPublicationYear())
        self.assertContains(response, self.book.publisher)
        self.assertContains(response, self.book.imageL)
        self.assertContains(response, 'Material Gworl2')

    def test_displays_3_review_message(self):
        review = BookReview.objects.create(
            creator=self.user1,
            book=self.book,
            title="Random rating Uno",
            book_rating=random.randrange(0, 10),
            content="Material Gworl1"
        )
        review = BookReview.objects.create(
            creator=self.user2,
            book=self.book,
            title="Random rating Dos",
            book_rating=random.randrange(0, 10),
            content="Material Gworl2"
        )
        review = BookReview.objects.create(
            creator=self.user3,
            book=self.book,
            title="Random rating Tres",
            book_rating=random.randrange(0, 10),
            content="Material Gworl3"
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail_view.html')
        content = response.content
        self.assertContains(response, 'Author')
        self.assertContains(response, self.book.ISBN)
        # this next test uses a specific value rather than accessing book.title
        # this is because the webpage formats the punctuation in the title differently
        # and I felt this was more suitable than spending time trying to convert.
        self.assertContains(response, "Arthur&#x27;s Tooth (Arthur Adventure Series)")
        self.assertContains(response, self.book.getPublicationYear())
        self.assertContains(response, self.book.publisher)
        self.assertContains(response, self.book.imageL)
        self.assertContains(response, "Material Gworl3")

    def test_displays_3_review_messages_when_more_than_3_reviews(self):
        review = BookReview.objects.create(
            creator=self.user1,
            book=self.book,
            title="Random rating Uno",
            book_rating=random.randrange(0, 10),
            content="Material Gworl1"
        )
        review = BookReview.objects.create(
            creator=self.user2,
            book=self.book,
            title="Random rating Dos",
            book_rating=random.randrange(0, 10),
            content="Material Gworl2"
        )
        review = BookReview.objects.create(
            creator=self.user3,
            book=self.book,
            title="Random rating Tres",
            book_rating=random.randrange(0, 10),
            content="Material Gworl3"
        )
        review = BookReview.objects.create(
            creator=self.user4,
            book=self.book,
            title="Random rating Quatro",
            book_rating=random.randrange(0, 10),
            content="Material Gworl4"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail_view.html')
        content = response.content
        self.assertContains(response, 'Author')
        self.assertContains(response, self.book.ISBN)
        # this next test uses a specific value rather than accessing book.title
        # this is because the webpage formats the punctuation in the title differently
        # and I felt this was more suitable than spending time trying to convert.
        self.assertContains(response, "Arthur&#x27;s Tooth (Arthur Adventure Series)")
        self.assertContains(response, self.book.getPublicationYear())
        self.assertContains(response, self.book.publisher)
        self.assertContains(response, self.book.imageL)
        self.assertContains(response, 'Material Gworl1')
        self.assertContains(response, 'Material Gworl2')
        self.assertContains(response, "Material Gworl3")
        self.assertNotContains(response, "Material Gworl4")

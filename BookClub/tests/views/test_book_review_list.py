from datetime import date

from django.test import TestCase, tag
from django.urls import reverse
import random
from BookClub.models import ClubMembership, Club, User, Book, BookReview

@tag('book','review','library')
class BookReviewListView(TestCase):
    
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
        self.url = reverse('book_reviews', kwargs={'book_id' : 54273})
        
    def test_url(self):
        self.assertEquals(self.url, "/library/books/"+str(54273)+"/reviews/")
        
    def test_no_reviews_returns_empty(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'book_reviews.html')
        context = response.context
        self.assertEqual(len(context.get('reviews')), 0)
        self.assertContains(response, "No reviews")    
        
    def test_displays_1_review_message(self):
        review = BookReview.objects.create(
            user = self.user1,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl1"               
        )

        response = self.client.get(self.url)        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_reviews.html')
        content = response.content
        # this next test uses a specific value rather than accessing book.title
        # this is because the webpage formats the punctuation in the title differently
        # and I felt this was more suitable than spending time trying to convert.
        self.assertContains(response, "Material Gworl1")
        
        
    def test_displays_2_review_message(self):
        review = BookReview.objects.create(
            user = self.user1,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl1"               
        )
        review = BookReview.objects.create(
            user = self.user2,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl2"               
        )
        response = self.client.get(self.url)        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_reviews.html')
        # this next test uses a specific value rather than accessing book.title
        # this is because the webpage formats the punctuation in the title differently
        # and I felt this was more suitable than spending time trying to convert.
        self.assertContains(response, "Material Gworl2")
        
    def test_displays_3_review_message(self):
        review = BookReview.objects.create(
            user = self.user1,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl1"               
        )
        review = BookReview.objects.create(
            user = self.user2,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl2"               
        )
        review = BookReview.objects.create(
            user = self.user3,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl3"               
        )
        
        response = self.client.get(self.url)        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_reviews.html')
        content = response.content
        self.assertContains(response, "Material Gworl3")
        
    def test_displays_3_review_messages_when_more_than_3_reviews(self):
        review = BookReview.objects.create(
            user = self.user1,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl1"               
        )
        review = BookReview.objects.create(
            user = self.user2,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl2"               
        )
        review = BookReview.objects.create(
            user = self.user3,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl3"               
        )
        review = BookReview.objects.create(
            user = self.user4,
            book = self.book,
            rating = random.randrange(0, 10),
            review = "Material Gworl4"               
        )
        response = self.client.get(self.url)        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_reviews.html')
        self.assertContains(response, "Material Gworl4")
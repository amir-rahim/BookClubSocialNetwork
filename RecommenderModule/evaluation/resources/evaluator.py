from collections import Counter

"""This class is responsible for evaluating recommendations, using LeaveOneOut test and train sets."""
class Evaluator:

    recommendations = []
    trainset = None
    left_out_test_set = []
    popularity_list = []

    def __init__(self, recommendations, trainset, left_out_test_set):
        self.recommendations = recommendations
        self.trainset = trainset
        self.left_out_test_set = left_out_test_set
        self.compute_list_books_sorted_by_most_read()


    """Compute all evaluations for the given recommendations, 
        and then print them through the print_evaluations() method."""
    def evaluate(self):
        hit_rate = self.get_hit_rate()
        average_reciprocal_hit_rate = self.get_average_reciprocal_hit_rate()
        novelty = self.get_novelty()
        self.print_evaluations(hit_rate, average_reciprocal_hit_rate, novelty)


    def print_evaluations(self, hit_rate, average_reciprocal_hit_rate, novelty):
        print()
        print(f" -> hit_rate:{hit_rate}")
        print(f" -> average_reciprocal_hit_rate:{average_reciprocal_hit_rate}")
        print(f" -> novelty:{novelty}")
        print()


    """Get the hit-rate of an algorithm, given the recommendations produced from
        the dataset's LOOCV train set and the left-out LOOCV test set."""
    def get_hit_rate(self):
        hits = 0
        total = len(self.left_out_test_set)

        for user_id, book_id, rating in self.left_out_test_set:

            # We increment the number of hits if the book has been recommended to the user
            try:
                if (book_id in self.recommendations[user_id]):
                    hits += 1
            except:
                pass

        return hits / total


    """Get the average reciprocal (weighted) hit-rate of an algorithm, given the
        recommendations produced from the dataset's LOOCV train set and the
        left-out LOOCV test set."""
    def get_average_reciprocal_hit_rate(self):
        hits = 0
        total = len(self.left_out_test_set)

        for user_id, book_id, rating in self.left_out_test_set:

            try:

                # We increment the value of 'hits' if the book has been recommended to the user,
                # with a weighting corresponding to its rank in the recommendations
                rank = 1
                for recommended_book in self.recommendations[user_id]:
                    if (book_id == recommended_book):
                        hits += (1/rank)
                        break
                    rank += 1

            except:
                pass

        return hits / total


    """Get the novelty (mean popularity rank of recommended items) of an algorithm,
        given the recommendations produced from the dataset's LOOCV train set and
        the train set itself."""
    def get_novelty(self):

        sum = 0
        total = 0

        for (user_id, recommended_books) in self.recommendations.items():
            for isbn in recommended_books:
                try:
                    sum += self.popularity_list.index(isbn)
                    total += 1
                except: # The book is not in the popularity list, we consider its index as the last index of the list + 1
                    sum += len(self.popularity_list)
                total += 1

        if (total == 0):
            return 0
        return sum / total


    """Make a list of all books in the given trainset, sorted from the book with the most ratings to the one with the 
    fewest ratings (descending order)."""
    def compute_list_books_sorted_by_most_read(self):

        all_book_occurrences = []
        for user_inner_id, item_inner_id, rating in self.trainset.all_ratings():
            all_book_occurrences.append(self.trainset.to_raw_iid(item_inner_id))
        counter = Counter(all_book_occurrences)
        sorted_books = sorted(counter.items(), key=lambda item: item[1], reverse=True)
        self.popularity_list = [pair[0] for pair in sorted_books]
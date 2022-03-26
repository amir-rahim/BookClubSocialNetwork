from collections import Counter

class EvaluationMetrics:

    trainset = None
    testset = []
    popularity_list = []

    def __init__(self, trainset, testset):
        self.trainset = trainset
        self.testset = testset
        self.compute_list_books_sorted_by_most_read()


    """Make a list of all books in the given trainset, sorted from the book with the most ratings to the one with the 
    fewest ratings (descending order)."""
    def compute_list_books_sorted_by_most_read(self):
        all_book_occurrences = []
        for user_inner_id, item_inner_id, rating in self.trainset.all_ratings():
            all_book_occurrences.append(self.trainset.to_raw_iid(item_inner_id))
        counter = Counter(all_book_occurrences)
        sorted_books = sorted(counter.items(), key=lambda item: item[1], reverse=True)
        self.popularity_list = [pair[0] for pair in sorted_books]



    """Get the hit-rate of an algorithm, given the recommendations produced from
        the dataset's LOOCV train set and the left-out LOOCV test set."""
    def get_hit_rate(self, recommendations):
        hits = 0
        total = len(self.testset)

        for user_id, book_id, rating in self.testset:

            # We increment the number of hits if the book has been recommended to the user
            try:
                if book_id in recommendations[user_id]:
                    hits += 1
            except:
                pass

        return hits / total


    """Get the average reciprocal (weighted) hit-rate of an algorithm, given the
        recommendations produced from the dataset's LOOCV train set and the
        left-out LOOCV test set."""
    def get_average_reciprocal_hit_rate(self, recommendations):
        hits = 0
        total = len(self.testset)

        for user_id, book_id, rating in self.testset:

            try:

                # We increment the value of 'hits' if the book has been recommended to the user,
                # with a weighting corresponding to its rank in the recommendations
                rank = 1
                for recommended_book in recommendations[user_id]:
                    if book_id == recommended_book:
                        hits += (1/rank)
                        break
                    rank += 1

            except:
                pass

        return hits / total


    """Get the novelty (mean popularity rank of recommended items) of an algorithm,
        given the recommendations produced from the dataset's LOOCV train set and
        the train set itself."""
    def get_novelty(self, recommendations):

        sum = 0
        total = 0

        for (user_id, recommended_books) in recommendations.items():
            for isbn in recommended_books:
                try:
                    sum += self.popularity_list.index(isbn) + 1 # We add 1 to account for the fact that the first book in the list has index 0
                except: # The book is not in the popularity list, we consider its index as the last index of the list + 1
                    sum += len(self.popularity_list) + 1 # We add 1 to account for the fact that the first book in the list has index 0
                total += 1

        if total == 0:
            return 0
        return sum / total

    """Get the rate of correct recommendations ('true positives') of an algorithm, given the recommendations produced 
        from the dataset's LOOCV train set and the left-out LOOCV test set.
        The rate is calculated as the number of recommended books that are correctly part of the testset
        out of the total number of books recommended."""
    def get_precision(self, recommendations):

        hits = 0
        total = 0

        for user in recommendations.keys():
            user_recommendations = recommendations[user]
            total += len(user_recommendations)

        for user_id, book_id, rating in self.testset:

            # We increment the number of hits if the book has been recommended to the user
            try:
                if book_id in recommendations[user_id]:
                    hits += 1
            except:
                pass

        if total == 0:
            return 0
        return hits / total


    """Get the rate of users that can get recommendations using the evaluated recommender algorithm,
        given the recommendations produced from the dataset's LOOCV train set and the left-out LOOCV test set.
        The rate is calculated as the number of users given recommendations divided by the total number of users in the testset."""
    def get_recommendation_eligible_users_rate(self, recommendations):
        eligible_users_number = len([(user, user_recommendations) for (user, user_recommendations) in recommendations.items() if user_recommendations != []])
        all_users_number = self.trainset.n_users
        return eligible_users_number / all_users_number


    """Percentage of users having at least 1 'good' recommendation.
        given the recommendations produced from the dataset's LOOCV train set and the left-out LOOCV test set."""
    def get_user_coverage(self, recommendations):

        users_number = len(recommendations)

        good_recommendation_users = set()
        for user_id, book_id, rating in self.testset:

            # We add the user to good_recommendation_users if the book has been recommended to the user
            try:
                if book_id in recommendations[user_id]:
                    good_recommendation_users.add(user_id)
            except:
                pass

        return len(good_recommendation_users) / users_number


    """Get F1 score (harmonic mean of precision and recall),
        given the recommendations produced from the dataset's LOOCV train set and the left-out LOOCV test set."""
    def get_f1_score(self, recommendations):
        precision = self.get_precision(recommendations)
        recall = self.get_hit_rate(recommendations)
        f1_score = 2 * (precision * recall) / (precision + recall)
        return f1_score
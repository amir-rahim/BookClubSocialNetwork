from RecommenderModule.recommenders.resources.popular_books_recommender_methods import PopularBooksMethods

"""Get the hit-rate of an algorithm, given the recommendations produced from
    the dataset's LOOCV train set and the left-out LOOCV test set."""
def get_hit_rate(recommendations, left_out_test_set):
    hits = 0
    total = len(left_out_test_set)

    for user_id, book_id, rating in left_out_test_set:

        # We increment the number of hits if the book has been recommended to the user
        try:
            if (book_id in recommendations[user_id]):
                hits += 1
        except:
            pass

    return hits / total


"""Get the average reciprocal (weighted) hit-rate of an algorithm, given the
    recommendations produced from the dataset's LOOCV train set and the
    left-out LOOCV test set."""
def get_average_reciprocal_hit_rate(recommendations, left_out_test_set):
    hits = 0
    total = len(left_out_test_set)

    for user_id, book_id, rating in left_out_test_set:

        try:

            # We increment the value of 'hits' if the book has been recommended to the user,
            # with a weighting corresponding to its rank in the recommendations
            rank = 1
            for recommended_book in recommendations[user_id]:
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
def get_novelty(recommendations, trainset):

    popular_books = PopularBooksMethods(trainset=trainset)
    popularity_list = popular_books.sorted_average_ratings

    sum = 0
    total = 0

    for (user_id, recommended_books) in recommendations.items():
        for isbn in recommended_books:
            try:
                sum += popularity_list.index(isbn)
            except: # The book is not in the popularity list, we consider its index as the last index of the list + 1
                sum += len(popularity_list)
            total += 1

    if (total == 0):
        return 0
    return sum / total

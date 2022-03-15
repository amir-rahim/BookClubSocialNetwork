from collections import Counter

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

    # Get a list of all books in the trainset, sorted from the book with the most ratings to the one with the fewest ratings
    popularity_list = get_books_sorted_by_most_read(trainset)

    sum = 0
    total = 0

    for (user_id, recommended_books) in recommendations.items():
        for isbn in recommended_books:
            try:
                sum += popularity_list.index(isbn)
                total += 1
            except: # The book is not in the popularity list, we consider its index as the last index of the list + 1
                sum += len(popularity_list)
            total += 1

    if (total == 0):
        return 0
    return sum / total


"""Get a list of all books in the given trainset, sorted from the book with the most ratings to the one with the fewest ratings (descending order)."""
def get_books_sorted_by_most_read(trainset):

    all_book_occurrences = []
    for user_inner_id, item_inner_id, rating in trainset.all_ratings():
        all_book_occurrences.append(trainset.to_raw_iid(item_inner_id))
    counter = Counter(all_book_occurrences)
    sorted_books = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    return [pair[0] for pair in sorted_books]
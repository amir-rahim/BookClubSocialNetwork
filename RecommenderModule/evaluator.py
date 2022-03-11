"""Get the hit-rate of an algorithm, given the recommendations produced from
    the dataset's LOOCV train set and the left-out LOOCV test set."""
def get_hit_rate(recommendations, left_out_test_set):
    hits = 0
    total = 0

    for inner_user_id, inner_item_id, rating in left_out_test_set:
        user_id = left_out_test_set.to_raw_uid(inner_user_id)
        book_id = left_out_test_set.to_raw_iid(inner_item_id)

        # We increment the number of hits if the book has been recommended to the user
        if (book_id in recommendations[user_id]):
            hits += 1

        total += 1

    # Check whether can remove 'total' increment in loop (TO BE REMOVED)
    print(total == len(left_out_test_set))

    return hits / total


"""Get the average reciprocal (weighted) hit-rate of an algorithm, given the
    recommendations produced from the dataset's LOOCV train set and the
    left-out LOOCV test set."""
def get_average_reciprocal_hit_rate(recommendations, left_out_test_set):
    hits = 0
    total = 0

    for inner_user_id, inner_item_id, rating in left_out_test_set:
        user_id = left_out_test_set.to_raw_uid(inner_user_id)
        book_id = left_out_test_set.to_raw_iid(inner_item_id)

        # We increment the value of 'hits' if the book has been recommended to the user,
        # with a weighting corresponding to its rank in the recommendations
        rank = 1
        for recommended_book in recommendations[user_id]:
            if (book_id == recommended_book):
                hits += (1/rank)
                break
            rank += 1

        total += 1

    # Check whether can remove 'total' increment in loop (TO BE REMOVED)
    print(total == len(left_out_test_set))

    return hits / total

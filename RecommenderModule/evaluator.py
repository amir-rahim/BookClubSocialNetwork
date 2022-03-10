"""Get the hit-rate of an algorithm, given the recommendations produced from
    the dataset's LOOCV train set and the left-out LOOCV test set"""
def get_hit_rate(recommendations, left_out_test_set):
    hits = 0
    total = 0
    
    for left_out_item in left_out_test_set:
        user_id = left_out_item[0]
        book_id = left_out_item[1]
        # We increment the number of hits if the book has been recommended to the user
        if (book_id in recommendations[user_id]):
            hits += 1
        total += 1
        
    # Check whether can remove 'total' increment in loop
    print(total == len(left_out_test_set))
    
    return hits / total
import itertools
from surprise import accuracy
from collections import defaultdict
class MetricsTools:
    
    """
    RMSE returns the Root Mean Square Error of our set of predictions, using the surprise library to calculate.
    """
    def RMSE(predictions):
        return accuracy.rmse(predictions, verbose=False)
    """
    MSE returns the Mean Square Error of our set of predictions, using the surprise library to calculate.
    """
    def MSE(predictions):
        return accuracy.mse(predictions, verbose=False)
    
    """
    MAE returns the Mean Average Error of our set of predictions, using the surprise library to calculate.
    """
    def MAE(predictions):
        return accuracy.mae(predictions, verbose=False)
    
    """
    GetTopN gets the top N predictions and returns them as a defaultdict.
    """
    def GetTopN(predictions, n=10, minimumRating=5.0):
        topN = defaultdict(list)
        
        for userID, bookID, actualRating, predictedRating, _ in predictions:
            if(predictedRating>= minimumRating):
                topN[int(userID)].append((int(bookID), predictedRating))
                
        for userID, ratings in topN.items():
            ratings.sort(key=lambda x:x[1], reverse=True)
            topN[int(userID)] = ratings[:n]
            
        return topN
    """HitRate returns the hit rate of our prediction, by passing it our top n recommendations and the predictions we purposely left out of the training set
    """
    def HitRate(predictions, leftOutPredictions):
        
        hits = 0
        total = 0
        
        for leftOut in leftOutPredictions:
            userID = leftOut[0]
            leftOutBookID = leftOut[1]
            # Is it in the predicted top 10 for this user?
            hit = False
            for bookID, predictedRating in predictions[int(userID)]:
                if (int(leftOutBookID) == int(bookID)):
                    hit = True
                    break
            if (hit) :
                hits += 1

            total += 1

        # Compute overall precision
        return hits/total
    
    def CumulativeHitRate(predictions, leftOutPredictions, minimumRating = 5.0):
        hits = 0
        total = 0
        for userID, leftOutBookID, actualRating, estimatedRating, _ in leftOutPredictions:
            # Only look at ability to recommend things the users actually liked...
            if (actualRating >= minimumRating):
                # Is it in the predicted top 10 for this user?
                hit = False
                for movieID, predictedRating in predictions[int(userID)]:
                    if (int(leftOutBookID) == movieID):
                        hit = True
                        break
                if (hit) :
                    hits += 1

                total += 1

        # Compute overall precision
        return hits/total
    
    def RatingHitRate(topNPredicted, leftOutPredictions):
        hits = defaultdict(float)
        total = defaultdict(float)

        # For each left-out rating
        for userID, leftOutMovieID, actualRating, estimatedRating, _ in leftOutPredictions:
            # Is it in the predicted top N for this user?
            hit = False
            for movieID, predictedRating in topNPredicted[int(userID)]:
                if (int(leftOutMovieID) == movieID):
                    hit = True
                    break
            if (hit) :
                hits[actualRating] += 1

            total[actualRating] += 1

        # Compute overall precision
        for rating in sorted(hits.keys()):
            print (rating, hits[rating] / total[rating])

    def AverageReciprocalHitRank(topNPredicted, leftOutPredictions):
        summation = 0
        total = 0
        # For each left-out rating
        for userID, leftOutMovieID, actualRating, estimatedRating, _ in leftOutPredictions:
            # Is it in the predicted top N for this user?
            hitRank = 0
            rank = 0
            for movieID, predictedRating in topNPredicted[int(userID)]:
                rank = rank + 1
                if (int(leftOutMovieID) == movieID):
                    hitRank = rank
                    break
            if (hitRank > 0) :
                summation += 1.0 / hitRank

            total += 1

        return summation / total

    # What percentage of users have at least one "good" recommendation
    def UserCoverage(topNPredicted, numUsers, ratingThreshold=0):
        hits = 0
        for userID in topNPredicted.keys():
            hit = False
            for movieID, predictedRating in topNPredicted[userID]:
                if (predictedRating >= ratingThreshold):
                    hit = True
                    break
            if (hit):
                hits += 1

        return hits / numUsers
    
    def Novelty(topNPredicted, rankings):
        n = 0
        total = 0
        for userID in topNPredicted.keys():
            for rating in topNPredicted[userID]:
                movieID = rating[0]
                rank = rankings[movieID]
                total += rank
                n += 1
        return total / n
    
    def Diversity(topNPredicted, simsAlgo):
        n = 0
        total = 0
        simsMatrix = simsAlgo.compute_similarities()
        for userID in topNPredicted.keys():
            pairs = itertools.combinations(topNPredicted[userID], 2)
            for pair in pairs:
                movie1 = pair[0][0]
                movie2 = pair[1][0]
                innerID1 = simsAlgo.trainset.to_inner_iid(str(movie1))
                innerID2 = simsAlgo.trainset.to_inner_iid(str(movie2))
                similarity = simsMatrix[innerID1][innerID2]
                total += similarity
                n += 1

        S = total / n
        return (1-S)
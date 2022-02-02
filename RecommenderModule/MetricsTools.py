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
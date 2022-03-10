from surprise.model_selection import LeaveOneOut

"""This class provides the Evaluator Engine with a dataset split into a
    train set and a test set, using 'Leave-One-Out'."""
class EvaluationDataProvider:
    
    dataset = None
    loocv_trainset = None
    loocv_testset = None
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.build_loocv_datasets()
        
    """Split the original dataset to build 'Leave-One-Out' train and test sets
        for evaluating top-N recommenders."""
    def build_loocv_datasets(self):
        # Build a "leave one out" train/test split for evaluating top-N recommenders
        LOOCV = LeaveOneOut(n_splits=1, random_state=1)
        for loocv_trainset, loocv_testset in LOOCV.split(self.dataset):
            self.loocv_trainset = loocv_trainset
            self.loocv_testset = loocv_testset
            
    """Accessor method to get the train and test sets (as a pair) built from
        the original dataset, using 'Leave-One-Out'."""
    def get_loocv_datasets(self):
        return (self.loocv_trainset, self.loocv_testset)
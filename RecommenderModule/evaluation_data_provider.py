from surprise.model_selection import LeaveOneOut

"""This class provides the Evaluator Engine with a dataset split into a
    train set and a test set, using 'Leave-One-Out'."""
class EvaluationDataProvider:
    
    dataset = None
    loocv_trainset = None
    loocv_testset = None
    read_books_all_users = {}
    
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
    
    
    def build_read_books_all_users_dict(self):
        self.read_books_all_users = {}
        trainset = self.loocv_trainset
        for inner_user_id, inner_item_id, rating in trainset.all_ratings():
            print(f"{trainset.to_raw_uid(inner_user_id)} -> {trainset.to_raw_iid(inner_item_id)}")
            raw_user_id = trainset.to_raw_uid(inner_user_id)
            raw_item_id = trainset.to_raw_iid(inner_item_id)
            try:
                self.read_books_all_users[raw_user_id].append(raw_item_id)
            except:
                self.read_books_all_users[raw_user_id] = [raw_item_id]
    
    def get_read_books_all_users_dict(self):
        if (self.read_books_all_users == {}):
            self.build_read_books_all_users_dict()
        return self.read_books_all_users
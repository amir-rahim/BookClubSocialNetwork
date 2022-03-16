class AbstractRecommender:

    def train(self, trainset=None, parameters={}):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")

    def train_and_save(self, trainset=None, parameters={}):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")

    def get_recommendations(self, user_id):
        raise NotImplementedError("Attempting to use abstract method from BaseRecommender super class.")
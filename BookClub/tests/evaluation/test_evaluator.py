from django.test import TestCase, tag
from RecommenderModule.evaluation.evaluator import Evaluator

@tag('evaluation')
class EvaluatorTestCase(TestCase):

    def setUp(self):
        self.evaluator = Evaluator(print_status=False)

    def test_make_combinations_from_dict_single_parameter(self):
        parameters_dict = {
            "parameter 1": [1, 2, 3]
        }
        all_combinations = self.evaluator.make_combinations_from_dict(parameters_dict)
        self.assertEqual(all_combinations, [
            {"parameter 1": 1},
            {"parameter 1": 2},
            {"parameter 1": 3}
        ])

    def test_make_combinations_from_dict_multiple_parameters(self):
        parameters_dict = {
            "parameter 1": [1, 2],
            "parameter 2": [3, 4],
            "parameter 3": [4, 5, 6],
            "parameter 4": [3]
        }
        all_combinations = self.evaluator.make_combinations_from_dict(parameters_dict)
        self.assertEqual(all_combinations, [
            {'parameter 1': 1, 'parameter 2': 3, 'parameter 3': 4, 'parameter 4': 3},
            {'parameter 1': 1, 'parameter 2': 3, 'parameter 3': 5, 'parameter 4': 3},
            {'parameter 1': 1, 'parameter 2': 3, 'parameter 3': 6, 'parameter 4': 3},
            {'parameter 1': 1, 'parameter 2': 4, 'parameter 3': 4, 'parameter 4': 3},
            {'parameter 1': 1, 'parameter 2': 4, 'parameter 3': 5, 'parameter 4': 3},
            {'parameter 1': 1, 'parameter 2': 4, 'parameter 3': 6, 'parameter 4': 3},
            {'parameter 1': 2, 'parameter 2': 3, 'parameter 3': 4, 'parameter 4': 3},
            {'parameter 1': 2, 'parameter 2': 3, 'parameter 3': 5, 'parameter 4': 3},
            {'parameter 1': 2, 'parameter 2': 3, 'parameter 3': 6, 'parameter 4': 3},
            {'parameter 1': 2, 'parameter 2': 4, 'parameter 3': 4, 'parameter 4': 3},
            {'parameter 1': 2, 'parameter 2': 4, 'parameter 3': 5, 'parameter 4': 3},
            {'parameter 1': 2, 'parameter 2': 4, 'parameter 3': 6, 'parameter 4': 3}
        ])
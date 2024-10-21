import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import os
from os.path import join, dirname
from dotenv import load_dotenv
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        self.database_path = os.environ.get("TEST_DB_PATH")
        
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })

        self.client = self.app.test_client

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_create_question_success(self):
        dummy_question_data = {
            'question': 'How re u doing?',
            'answer': 'I am doing good!',
            'difficulty': 1,
            'category': 1}

        res = self.client().post('/questions', json=dummy_question_data)
        data = json.loads(res.data)

    def test_create_question_error(self):
        dummy_question_data = {
            # 'question': 'How re u doing?',
            'answer': 'I am doing good!',
            'difficulty': 1,
            'category': 1}

        res = self.client().post('/questions', json=dummy_question_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unable to process request')

    def test_get_questions_success(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['result'])
        self.assertTrue(data['total'])

    def test_get_questions_404(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_delete_question_success(self):
        dummy_question = Question(question='Hayy, Wassap?',
                                  answer='Woohoooo!!!',
                                  difficulty=1,
                                  category=1)

        dummy_question.insert()
        dummy_question_id = dummy_question.id
        res = self.client().delete('/questions/{}'.format(dummy_question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['result'], {"answer": dummy_question.answer,
                                          "category": dummy_question.category,
                                          "difficulty": dummy_question.difficulty,
                                          "id": dummy_question.id,
                                          "question": dummy_question.question})

    def test_delete_question_422(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unable to process request')

    def test_search_questions_found(self):
        new_search = {'search_term': 'how'}
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['result'])
        self.assertTrue(data['total'])

    def test_search_questions_404(self):
        bogus_search = {'search_term': ''}
        res = self.client().post('/questions/search', json=bogus_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_get_categories_success(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['result'])

    def test_get_categories_404(self):
        res = self.client().get('/categories/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_get_category_questions_success(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['result'])
        self.assertTrue(data['total'])
        self.assertTrue(data['current_category'])

    def test_get_category_questions_404(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
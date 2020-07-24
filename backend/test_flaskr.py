import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    app = create_app()

    def setUp(self):
        """Define test variables and initialize app."""
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format('yopiprabowooktiovan','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #test get questions endpoint
    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)
    
    # delete page endpoint
    #created by self with help from https://knowledge.udacity.com/questions/268503 for test error delete
    # def test_delete_questions(self):
    #     res = self.client().delete('/questions/8')
    #     data = json.loads(res.data)
    #     #Assersion
    #     self.assertEqual(res.status_code,200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['delete'], 8)

    def test_error_delete_questions(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    
    #Create questions endpoint
    def test_create_questions(self):
        question = {
            'question': 'Which team does Lionel Messi plays for?',
            'answer': 'FC Barcelona',
            'category': '2',
            'difficulty': '2'
        }
        #Post new question
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_error_create_questions(self):
        question = {
            'question': 'Lalalala',
            'answer': 'Llililili',
            'difficulty': '1000'
            }
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

    #Filter categories and questions endpoint
    def test_filter_categories(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'],None)

    def test_422_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    #Search Questions endpoint
    def test_search_questions(self):
        search_term = {'searchTerm': 'What boxer\'s original name is Cassius Clay?'}
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)

    def test_quiz_questions(self):
        #Got help from https://knowledge.udacity.com/questions/150173
        self.quiz_category = {
            'previous_questions': [],
            'quiz_category':{
                'type': 'Science',
                'id': 1
            }
        }
        res = self.client().post('/quizzes', json = self.quiz_category)
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
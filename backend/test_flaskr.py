from distutils.log import error
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
                "student", "student", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Wich team won the last Chmpions League",
                         "answer": "Real Madrid",
                         "category": "2",
                         "difficulty": 1}
        

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
    def test_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_404_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertEqual(question, None)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_422_sent_on_deleting_non_existing_question(self):
        res = self.client().delete("/questions/100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "request could not be processed")

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(len(data["questions"]))

    def test_422_if_question_creation_fails(self):

        res = self.client().post("/questions/3", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "request could not be processed")

    def test_get_question_search_with_results(self):
        res = self.client().post("/search", json={"searchTerm": "League"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 3)

    def test_get_book_search_without_results(self):
        res = self.client().post("/search", json={"searchTerm": "premiership"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(len(data["questions"]), 0)

    def test_retrieve_questions_on_category(self):
        res = self.client().get("/cat-questions?category='1'")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_questions_per_category(self):
        res = self.client().get('/categories/no_cat/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        new_quiz_round = {'previous_questions': [],
                          'quiz_category': {'type': 'Entertainment', 'id': 1}}

        res = self.client().post('/quiz', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_play_quiz(self):
        new_quiz_round = {'previous_questions': []}
        res = self.client().post('/quiz', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "request could not be processed")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
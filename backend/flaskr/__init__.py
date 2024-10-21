import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    CORS(app, resources={r'*': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers','GET, POST, PATCH, DELETE, OPTIONS')
        return response

    def return_val(success, result):
        return jsonify({
            'success': success,
            'result': result
        })

    def return_mval(success, result, total, category=None):
        return jsonify({
            'success': success,
            'result': result,
            'total': total,
            'current_category': category
        })

    @app.route('/categories', methods=['GET'])
    def get_categories():
        cats = Category.query.all()
        return return_val(True, cats)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.all()
        page_number = request.args.get('page', 1)

        start = (page_number - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions_by_page = questions[start:end]

        if len(questions_by_page) == 0:
            abort(404)

        return return_mval(True, questions_by_page, len(questions))

    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()

            return return_val(True, question)
        except Exception as e:
            print(str(e))
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        question = request.get_json().get('question')
        answer = request.get_json().get('answer')
        category = request.get_json().get('category')
        difficulty = request.get_json().get('difficulty')

        if question is None or answer is None or category is None or difficulty:
            abort(422)

        try:
            new_question = Question(
                question=question, 
                answer=answer, 
                category=category, 
                difficulty=difficulty)

            new_question.insert()
            return return_val(True, new_question)
        except Exception as e:
            print(str(e))
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search = request.get_json().get('search_term')

        if len(search) <= 0:
            abort(404)

        search_result = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
        return return_mval(True, search_result, len(search_result))

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id).all()

        if len(questions) == 0:
            abort(404)

        return return_mval(True, questions, len(questions), category_id)

    @app.route('/quiz', methods=['POST'])
    def quiz():
        try:
            new_question = None
            body = request.get_json()

            if not ('quiz_category' in body or 'previous_questions' in body):
                abort(422)

            cat = body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            available_questions = Question.query.filter_by(category=cat['id']).all()
            remove_questions(available_questions, previous_questions)
            random_value = random.randrange(0, len(available_questions))

            if len(available_questions) > 0:
                new_question = available_questions[random_value]
            else:
                abort(422)

            return return_val(True, new_question)

        except BaseException as e:
            print(str(e))
            abort(422)

    def remove_questions(available_questions, previous_questions):
        for q in available_questions:
            if q.question in previous_questions:
                available_questions.remove(q)
        return available_questions

    @app.errorhandler(404)
    def not_found(error):
        return return_error(404, 'Resource Not Found')

    @app.errorhandler(400)
    def bad_request(error):
        return return_error(400, 'Bad Request')

    @app.errorhandler(422)
    def unable_to_process(error):
        return return_error(422, 'Unable to process request')

    @app.errorhandler(500)
    def server_error(error):
        return return_error(500, 'Internal Server Error')

    def return_error(error, msg):
        return jsonify({
            'success': False,
            'error': error,
            'message': msg
        }), error

    return app

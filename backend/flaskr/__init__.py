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
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def return_categories():
    try:
      categories = Category.query.order_by(Category.type).all()
      categories_formatted = {category.id: category.type for category in categories}
      if categories is None:
        abort(404)
      return jsonify({
        'success': True,
        'categories': categories_formatted
      })
    except:
      abort(422)


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    try:
      page = request.args.get('page',1,type=int)
      start = (page - 1) * 10
      end = start + 10
      questions = Question.query.order_by(Question.id).all()
      categories = Category.query.order_by(Category.type).all()
      categories_formatted = {category.id: category.type for category in categories}
      formatted_questions = [question.format() for question in questions]
      # selections = list(map(Question.format, Question.query.all()))
      # current_questions = paginate_questions(request, selections)
      if len(questions) == 0:
        abort(404)
      return(jsonify({
        'success': True,
        'questions': formatted_questions[start:end],
        'categories': categories_formatted,
        'total_questions': len(formatted_questions),
        'current_category': None
      }))
    except:
      abort(422)


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      
      question.delete()
      selection = Question.query.order_by(Question.id).all()

      return (jsonify({
        'success': True,
        'delete': question_id
      }))
    except:
      abort(422)



  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_questions():
    try:
      body = request.get_json()
      if not body:
        abort(400)
      new_question = body.get('question',None)
      new_answer = body.get('answer',None)
      new_categories = body.get('category',None)
      new_difficulty = body.get('difficulty',None)
      question = Question(question=new_question, answer=new_answer,
                    category=new_categories, difficulty=new_difficulty)
      question.insert()
      category_type = Category.query.get(new_categories).type
      result = {
        'success': True,
        'questions': question.question,
        'total_questions':len(Question.query.all()),
        'current_category':category_type
      }
    except:
      abort(400)
    return jsonify(result)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    try:
      page = request.args.get('page',1,type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      body = request.get_json()
      search_term = body.get('searchTerm',None)
      result = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
      formatted_questions = [question.format() for question in result]
      return jsonify({
        'success': True,
        'questions': formatted_questions[start:end],
        'total_questions': len(result),
        'current_category': None
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def filter_categories(category_id):
    try:
      page = request.args.get('page',1,type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      questions = Question.query.filter(Question.category == category_id).all()
      formatted_questions = [question.format() for question in questions]
      if len(questions) == 0:
        abort(404)
      return (jsonify({
        'success': True,
        'questions': formatted_questions[start:end],
        'total_questions': len(formatted_questions),
        'current_category': None
      }))
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  #Created with help from https://knowledge.udacity.com/questions/234306
  def create_quizzes():
    body = request.get_json()
    try:
      if not body:
        abort(400)
      previous = body.get('previous_questions', [])
      category = body.get('quiz_category','')

      if previous:
        if category:
          if category['id'] == 0:
            questions = Question.query.filter(~Question.id.in_(previous)).all()
          else:
            questions = Question.query.filter(Question.category == category['id']).filter(~Question.id.in_(previous)).all()
          question_format = [q.format() for q in questions]
          if len(questions) != 0:
            random_result = random.choice(question_format)
            return jsonify({
              'success': True,
              'question': random_result,
            })
          else:
            return jsonify({
              'question':False
            })
      else:
        if category:
          if category['id'] == 0:
            questions = Question.query.all()
          else:
            questions = Question.query.filter(Question.category == category['id']).all()
          question_format = [q.format() for q in questions]
          if len(questions) != 0:
            random_result = random.choice(question_format)
            return jsonify({
              'success': True,
              'question': random_result,
            })
          else:
            return jsonify({
              'question':False
            })
    except:      
      abort(422)



  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found_error(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'not_found'
    }), 404
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success':False,
      'error': 422,
      'message': 'unprocessable'
    }), 422
  
  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    })

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    })
  
  return app

    
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
  CORS(app)
  

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    formatted = [category.format() for category in categories]

    if(len(categories) == 0):
      abort(404)

    return jsonify({
      'success': True,
      'categories': formatted,
    }), 200


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

  def paginate(request, question_list):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    questions = [question.format() for question in question_list]
    return questions[start:end]

  @app.route('/questions')
  def get_questions():
    all_questions = Question.query.all()
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    questions = paginate(request, all_questions)

    if(len(questions) == 0):
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions,
      'categories': formatted_categories,
      'current_category': None,
      'total_questions': len(all_questions),
    }), 200
    


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question_id is None:
      abort(404)

    question.delete()

    all_questions = Question.query.all()
    questions = paginate(request, all_questions)
    
    return jsonify({
      'success': True,
      'deleted': question.id,
      'questions': questions,
      'total_questions': len(all_questions)
    })

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
  def post_question():
    body = request.get_json()
    
    question = body.get('question', None)
    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)
    
    if question is None or answer is None or category is None or difficulty is None:
      abort(400)
    try:
      new_question = Question(question=question, answer=answer, category=category, difficulty=int(difficulty))
      new_question.insert()

      return jsonify({
        'success': True,
        'created': new_question.id
      }), 201
    except:
      abort(422)




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
  def search_question():
    body = request.get_json()
    searchTerm = body.get('searchTerm', None)
    
    if searchTerm is None:
      abort(400)

    search = "%{}%".format(searchTerm)
    try:
      questions = Question.query.filter(Question.question.ilike(search)).all()
      return jsonify({
        'success': True,
        'questions': paginate(request, questions),
        'total_questions': len(questions)
      }), 200
    except:
      abort(500)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_categories(category_id):
    if category_id is None:
      abort(400)

    try:
      questions = Question.query.filter(Question.category == category_id).all()

      return jsonify({
        'success': True,
        'questions': paginate(request, questions),
        'total_questions': len(questions)
      }), 200
    
    except:
      abort(500)


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
  def get_quizzes():
    body = request.get_json()
    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')

    if previous_questions is None:
      previous_questions = []

    try:
      questions = []
      if quiz_category is None or quiz_category['id'] == 0:
        questions = Question.query.all()
      else:
        questions = Question.query.filter(Question.category == quiz_category['id']).all()
      
      n = random.randrange(len(questions))
      if len(previous_questions) > 0:
        while n in previous_questions:
          n = random.randrange(len(questions))
      
      question = questions[n].format()

      return jsonify({
        'success': True,
        'question': question,
      }), 200
    
    except:
      abort(500)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": 'Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": 'Unprocessable'
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad request'
    }), 400

  @app.errorhandler(405)
  def not_allow(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method not allowed'
    }), 405
  
  return app

    
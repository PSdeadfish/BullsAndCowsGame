from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, url_for
from App.models import db, CurrentGame, User
from App.controllers import create_user, login, get_user
import random
from datetime import date, datetime

index_views = Blueprint('index_views', __name__, template_folder='../templates')

#function to generate the secret number
def generate_secret_number():
    # Use the current date to seed the random number generator
    today = date.today()
    random.seed(today.strftime("%Y%m%d"))

    # Generate a list of unique random digits
    secret_digits = random.sample(range(10), 4)
    #return secret_digits
    
    # Convert the list of digits to a string --> only used if its being compared to a string
    secret_number = ''.join(map(str, secret_digits))
    return secret_number

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('login.html')

@index_views.route('/init', methods=['GET'])
def init():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bobpass')
    return jsonify(message='db initialized!')

# @index_views.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({'status':'healthy'})

# used on login page to redirect to the signup page alone
@index_views.route("/signup", methods=['GET'])
def signup_page():
    return render_template("signup.html")

@index_views.route("/game", methods=['GET'])
def game_page():
    #generate the secret number for the game
    secret_number = generate_secret_number()
    new_game = CurrentGame(userID=1,  secretNumber = secret_number, is_Won = False)
    return render_template("game_play.html")
        

@index_views.route("/leaderboard", methods=['GET'])
def leaderboard_page():
    return render_template("leaderboard.html")

#submit guess route
@index_views.route("/submit_guess", methods=['POST'])
def submit_guess():
    try:
        user_guess = request.form.get ('user_guess')
        current_game = CurrentGame.query.first()
        if current_game is None:
            return jsonify(message="No current game found"), 404
            
        if current_game.is_Won:
            return jsonify(message="Game is already won. You cannot submit more guesses.")
            
        if current_game.is_game_over(user_guess):
            current_game.is_Won = True
            user_guesses = UserGuesses(userID=current_game.userID, gameID=current_game.id, guess=user_guess)
            db.session.add(user_guesses)
            db.session.commit()
            return jsonify(message="Congratulations! You guessed the correct number.")
            
        bulls, cows = current_game.check_guess(user_guess)
        user_guesses = UserGuesses(userID=current_game.userID, gameID=current_game.id, guess=user_guess)
        user_guesses.bullsCount = bulls
        user_guesses.cowsCount = cows
        db.session.add(user_guesses)
        db.session.commit()
        return jsonify(message="Incorrect guess. Keep trying!")
    except Exception as e:
        return jsonify(message="An error occurred: {}".format(str(e))), 500
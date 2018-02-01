"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/users/<user_id>')
def display_user_details(user_id):
    """ Show user details"""

    user = User.query.get(user_id)
    return render_template("user_details.html", user=user)


@app.route('/movies')
def movie_list():
    """Show list of movies"""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


# @app.route('/movies/<movie_id>')
# def display_movie_details(movie_id):
#     """Show movie details"""

#     movie = Movie.query.get(movie_id)
#     return render_template("movie_details.html", movie=movie)


@app.route("/movies/<int:movie_id>", methods=['GET'])
def movie_detail(movie_id):
    """Show info about movie.

    If a user is logged in, let them add/edit a rating.
    """

    movie = Movie.query.get(movie_id)

    user_id = session.get("user_id")

    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    # Get average rating of movie

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    # Prediction code: only predict if the user hasn't rated it.

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)
            # above line - predict rating is a method with the user obj

    return render_template(
        "movie_details.html",
        movie=movie,
        user_rating=user_rating,
        average=avg_rating,
        prediction=prediction
        )


@app.route('/new_rating', methods=['POST'])
def update_rating():
    """Update a rating """

    movie_id = int(request.form.get("movie_id"))
    score = int(request.form.get('score'))
    user_id = session['user_id']

    rating = db.session.query(Rating).filter(Rating.user_id == user_id, Rating.movie_id == movie_id).first()

    if not rating:
        rating = Rating(movie_id=movie_id, user_id=user_id, score=score)
        db.session.add(rating)
        db.session.commit()
    else:
        rating.score = score
        db.session.commit()

    flash('You\'ve successfully rated for the movie!')

    return redirect("/movies/" + str(movie_id))


@app.route('/register', methods=['GET'])
def register_form():
    """For user to register with email"""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Get user registration and redirect to hp"""

    email = request.form.get("email")
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')

    user = db.session.query(User).filter(User.email == email).first()

    if not user:
        # if the user does not exist then we instantiate a user and the info
        #to the db
        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()

    session['user_id'] = user.user_id
    flash('You successfully registerd and logged in')
    return redirect("/users/" + str(user.user_id))


@app.route('/login', methods=['GET'])
def login_input():
    """For user to login with email"""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def check_login():
    """Check user login info"""

    email = request.form.get("email")
    password = request.form.get('password')

    check_db = db.session.query(User).filter(User.email == email, User.password == password)

    user = check_db.first()

    if not user:
        flash('Please regirster your account')

        return redirect('/register')
    else:
        session['user_id'] = user.user_id
        flash('You successfully logged in')
        return redirect('/users/' + str(user.user_id))


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')

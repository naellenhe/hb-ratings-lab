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
    return render_template("user_list.html", users= users)

@app.route('/users/<user_id>')
def display_user_details(user_id):
    """ Show user details"""

    user = db.session.query(User).filter(User.user_id == user_id).first()
    return render_template("user_details.html", user = user)


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

    check_db = db.session.query(User).filter(User.email == email)

    user_exist = check_db.first()

    if not user_exist:
        # if the user does not exist then we instantiate a user and the info
        #to the db
        user = User(email=email, password=password, age=age,zipcode=zipcode)
        db.session.add(user)
        db.session.commit()

    return redirect("/login")


@app.route('/login', methods=['GET'])
def login_input():
    """For user to login with email"""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def check_login():
    """Check user login info"""

    email = request.form.get("email")
    password = request.form.get('password')

    check_db = db.session.query(User).filter(User.email == email, User.password==password)

    user = check_db.first()

    if not user:
        return redirect('/register')
    else:
        session['user_id'] = user.user_id
        flash('You successfully logged in')
        return render_template('/', )



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


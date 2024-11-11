###############################################################################
#                         IMPORT REQUIRED LIBRARIES/MODULES
###############################################################################
# 1. The FLASK framework (the webserver)
from flask import Flask

# 2. For opening and read the HTML file and showing them as the webpage
from flask import render_template

# 3. From the flask library import the request class.
# Allows us to get information from the website URL
from flask import request

# 4. From the objects.py containing our classes for this application, only import the Movie class
from objects import Movie

# 5. Import the sqlite library
# SQLITE is NOT imported here. I do not have any SQL in this file
# import sqlite3

# 6. Instantiate the Flask() class and called it app
app=Flask(__name__)

###############################################################################
#                         CREATE YOUR WEBPAGE ROUTES
###############################################################################

# -----------------------------------------------------------------------------
# A) Create your home page.  Let's call the page "index"
# -----------------------------------------------------------------------------

#   Start with a decorator with no name. That way when they only type in your server's name
#   It will got to this page
@app.route("/")




# -----------------------------------------------------------------------------
# B) Create a page to DELETE records
#------------------------------------------------------------------------------

# Create a decorator with the route/path "delete".
# IMPORTANT: THIS IS A FORM!!!
# Allowable Actions:
#   GET:  This is when you first come to the page
#   POST: This is when you SUBMIT the information that you filled out in the form
@app.route("/index", methods=["GET","POST"]) # Decorator - Now

#   Define what should happen when visiting this page by using a function called index()
def index():


    if request.method == "GET":  # When you first visit the page

        # B1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        mList=Movie.getAllMovies()
        return render_template('index.html',message=mList)

    elif request.method == "POST": # When you fill out the form and click SUBMIT
        # Get the value from the form object called "movtitle" (it is a textbox)

        Title = request.form["Title"]

        # B1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        mList=Movie.getAllMovies()
        Movie.index(Title)

        # B1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        mList=Movie.getAllMovies()

        #Return the template index.html but pass it the list of movies
        # stored in the variable mList
        return render_template('add.html',message=mList )

    else:
        # How could it have not been a GET or POST? Hmm. Should have been one of them.
        return render_template('index.html',message="Something did not work.")
    
def add():
    if request.method == "GET":  # When you first visit the page

        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        mList=Movie.getAllMovies()
        return render_template('index.html',message=mList)

    elif request.method == "POST": # When you fill out the form and click SUBMIT
        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        mList=Movie.getAllMovies()

        # Get the value from the form object called "movtitle" (it is a textbox)
        title = request.form.get("movtitle", 0)

        # Get the value from the form object called "movyear" (it is a textbox)
        # This is an INTEGER. Quick, change it from TEXT to INTEGER using int() function
        year = int(request.form.get("movyear", 0))

        # Get the value from the form object called "movtitle" (it is a textbox)
        ImageName = request.form.get("ImageName", 0)

        # Run the function called saveMovieDB passing the method the title of the movie
        #   and the year the movie was release
        Movie.saveMovieDB(title, year, ImageName)

        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        mList=Movie.getAllMovies()

        #Return the template index.html but pass it the list of movies
        # stored in the variable mList
        return render_template('index.html',message=mList )

    else:
        # How could it have not been a GET or POST? I have no idea how that could have happened.
        return render_template('index.html',message='Something went wrong.')


#------------------------------------------------------------------------------------
# C) Create a page to INSERT records
#------------------------------------------------------------------------------------

@app.route("/edit", methods=["GET","POST"])
def edit():
    if request.method == "GET":  # When you first visit the page

        # B1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        mList=Movie.getAllMovies()
        return render_template('edit.html',message=mList)

    elif request.method == "POST": # When you fill out the form and click SUBMIT
        # Get the value from the form object called "movtitle" (it is a textbox)
        Title = request.form["name"]

        # B1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        mList=Movie.getAllMovies()
        Movie.index(Title)

        # B1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        mList=Movie.getAllMovies()

        #Return the template index.html but pass it the list of movies
        # stored in the variable mList
        return render_template('edit.html',message=mList )

    else:
        return render_template('edit.html')


app.run(debug=True)
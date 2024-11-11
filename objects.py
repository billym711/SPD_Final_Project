# A. Import the sqlite library
import sqlite3

class Movie:
    # 1. Create the constructor function
    def __init__(self, title="", year=1901):
        self.__title = title
        self.__year = year

    #######################################################
    # 1. ADD STANDARD PROPERTY DECORATORS
    #######################################################
    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        # You can add validation logic here if needed
        self.__title = value

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, value):
        # You can add validation logic here if needed
        self.__year = value

    #######################################################
    # 2. Create a function that returns the title and year released
    #######################################################
    #def getStr(self):
    def __str__(self):
        # Example string returned by this function
        #
        #        "Monty Python and the Holy Grail (1975)"
        #
        return self.title + " ("  + str(self.year) + ")"



    #######################################################
    # CREATE 3 CLASS METHONDS
    #######################################################

    # 3. DELETE MOVIE FROM DB by Title
    #######################################################
    @classmethod
    def index(cls, Title):
        #A. Make a connection to the database
        conn = None
        conn = sqlite3.connect( "birthdays.db")
        sql='DELETE FROM birthdays WHERE Name=?'
        cur = conn.cursor()
        cur.execute(sql, (Title,))
        conn.commit()
        conn.close()


    #######################################################
    # 4. ADD MOVIE TO DB
    #######################################################
    @classmethod
    def saveMovieDB(cls, Title, Year, ImageName):
        #A. Make a connection to the database
        conn = None
        conn = sqlite3.connect( "birthdays.db")

        #B. Write a SQL statement to insert a specific row (based on Title name)
        sql='INSERT INTO movies (Title, YearReleased, ImageName) values (?,?,?)'

        # B. Create a workspace (aka Cursor)
        cur = conn.cursor()

        # C. Run the SQL statement from above and pass it 1 parameter for each ?
        cur.execute(sql, (Title,Year,ImageName, ))

        # D. Save the changes
        conn.commit()
        if conn:
            conn.close()

    #######################################################
    # 5.              Create another CLASS method.
    #######################################################
    #   THIS IS NOT AN OBJECT METHOD
    #   This was made to be a CLASS level because if affects ALL movies
    #   and simply helps be retrive all movies (not just one)
    #   THIS RETURNS AS LIST OF DICTIONARIES
    @classmethod
    def getAllMovies(cls):
        # A. Connection to the database
        conn = sqlite3.connect('birthdays.db')

        # B. Create a workspace (aka Cursor)
        cursorObj = conn.cursor()

        # D. Run the SQL Select statement to retive the data
        cursorObj.execute('SELECT name, month, day FROM birthdays;')

        # E. Tell Pyton to 'fetch' all of the records and put them in
        #     a list called allRows
        allRows = cursorObj.fetchall()

        movieListOfDictionaries = []

        for individualRow in allRows:
            m = {"Title" : individualRow[0], "Year": individualRow[1], "Image":individualRow[2] }
            movieListOfDictionaries.append(m)

        if conn:
            conn.close()

        return movieListOfDictionaries

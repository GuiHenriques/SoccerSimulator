from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL
from random import randint

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    """Show main page"""
    teams = db.execute("SELECT team, color, rating FROM teams")
    cteams = db.execute("SELECT team, color, rating FROM cteams WHERE user_id = ?", 3)

    # db.execute("UPDATE teamsint SET color = '#' where team like '%'")

    return render_template("index.html", teams=teams, cteams=cteams)


@app.route("/search")
def search():
    """Filter teams"""
    q = str(request.args.get("q"))
    t = str(request.args.get("t"))

    cteams = db.execute("SELECT team, color FROM cteams WHERE user_id = ?", 1)
    teams = db.execute("SELECT team, color FROM ? WHERE team LIKE ?", t, "%" + q + "%")
    return render_template("search.html", teams=teams, cteams=cteams)


@app.route("/change")
def change():
    """Change the select options"""
    t = str(request.args.get("t"))
    try:
        cteams = db.execute("SELECT team, color FROM cteams WHERE user_id = ?", 1)
    except:
        cteams = []
    teams = db.execute("SELECT team, color FROM ?", t)

    return render_template("change.html", teams=teams, cteams=cteams)


@app.route("/match", methods=["GET", "POST"])
def match():
    """Show match statistics"""
    # Dictionay to store processed data
    stats = {}

    # Get all inputs
    teamType = request.form.get("team-type")
    advantage = request.form.get("home-advantage")

    stats["team1"] = request.form.get("team-name1")
    stats["team2"] = request.form.get("team-name2")

    # Check if all forms were submited
    if not teamType:
        return render_template("apology.html", message="Can't simulate match. Missing input field")

    # Get team 1 row:
    try:
        info1 = db.execute("SELECT * FROM ? WHERE Team = ?", teamType, stats["team1"])[0]
    except:
        try:
            info1 = db.execute("SELECT * FROM cteams WHERE Team = ?", stats["team1"])[0]
        except:
            return render_template("apology.html", message="No Home Team was selected")

    # Get team 2 row:
    try:
        info2 = db.execute("SELECT * FROM ? WHERE Team = ?", teamType, stats["team2"])[0]
    except:
        try:
            info2 = db.execute("SELECT * FROM cteams WHERE Team = ?", stats["team2"])[0]
        except:
            return render_template("apology.html", message="No Away Team was selected")

    # Win probability
    fifty = 50

    rating1 = float(info1["Rating"])
    rating2 = float(info2["Rating"])

    if advantage:
        rating1 += 5

    rat_diff = rating1 - rating2
    stats["percent1"] = round((fifty + rat_diff), 1)
    stats["percent2"] = round((fifty - rat_diff), 1)

    # Shots
    stats["goals1"] = round((int(info1["Goals"])/36) + randint(5, 15))
    stats["goals2"] = round((int(info2["Goals"])/36) + randint(5, 15))

    # Possession
    posse1 = float(info1["Possession%"])
    posse2 = float(info2["Possession%"])

    posse_diff = posse1 - posse2
    stats["posse1"] = round((fifty + posse_diff), 1)
    stats["posse2"] = round((fifty - posse_diff), 1)

    # Pass
    stats["pass1"] = float(info1["Pass%"]) + randint(-5, 5)
    stats["pass2"] = float(info2["Pass%"]) + randint(-5, 5)

    # Yellow Cards
    stats["cards1"] = round((int(info1["yellow_cards"]) / 38) + randint(-3, 1))
    stats["cards2"] = round((int(info2["yellow_cards"]) / 38) + randint(-3, 1))

    if stats["cards1"] < 0:
        stats["cards1"] = 0
    if stats["cards2"] < 0:
        stats["cards2"] = 0

    # Colors
    stats["color1"] = info1["color"]
    stats["color2"] = info2["color"]

    return render_template("match.html", stats=stats)


@app.route("/tournament", methods=["GET", "POST"])
def tournament():
    """Simulates a tournament"""
    if request.method == "POST":

        type = request.form.get("tour-type")
        if not type:
            return render_template("apology.html", message="No Tournament was Select")

        # Get Tournament Database

        if type == 'teamsbr' or type == 'teamsint':
            teams = db.execute("SELECT Team, color, Rating FROM ? ORDER BY Rating DESC", type)
            sum = float(db.execute("SELECT SUM(Rating) FROM ?", type)[0]['SUM(Rating)'])

        else:
            teams = db.execute("SELECT Team, color, Rating FROM teams WHERE Tournament = ? ORDER BY Rating DESC", type)
            sum = float(db.execute("SELECT SUM(Rating) FROM teams WHERE Tournament = ?", type)[0]['SUM(Rating)'])

        return render_template("tournamented.html", teams=teams, sum=sum)

    else:
        return render_template("tournament.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    """Create a team"""
    try:
        if session["user_id"]:
            pass
    except:
        return render_template("apology.html", message="You must be logged in to create a team")

    if request.method == "POST":
        cteam = request.form.get("cteam")
        crating = request.form.get("crating")
        ccolor = request.form.get("ccolor")
        cposse = request.form.get("cposse")

        # Check if all input fields were submited
        if not cteam or not crating or not ccolor or not cposse:
            return render_template("apology.html", message="Missing input field")

        if cteam == " " or crating == " " or ccolor == " " or cposse == " ":
            return render_template("apology.html", message="Missing input field")

        crating = int(crating)
        cposse = int(cposse)

        if crating > 100 or crating < 0:
            return render_template("apology.html", message="Rating must be from 0 to 100")

        if cposse < 0 or cposse > 100:
            return render_template("apology.html", message="Possession must be from 0 to 100")

        # Adapting the data

        ccolor = ccolor.upper()
        if len(ccolor) != 6:
            return render_template("apology.html", message="Hex color must be six digits")

        ccolor = "#" + ccolor

        # Insert new team into database
        try:
            db.execute("INSERT INTO cteams (user_id, Team, Rating, 'Possession%', color) VALUES(?, ?, ?, ?, ?)", session["user_id"], cteam, crating, cposse, ccolor)
        except:
            return render_template("apology.html", message="Couldnt insert team")

        return redirect("/created")

    else:
        # GET
        return render_template("create.html")

@app.route("/created")
def created():
    """Show existing Teams"""
    try:
        if session["user_id"]:
            pass
    except:
        return render_template("apology.html", message="You must be logged in to see your teams")

    cteams = db.execute("SELECT Team, team_id, color, Rating FROM cteams WHERE user_id = ?", session["user_id"])

    return render_template("created.html", cteams=cteams)

@app.route("/delete", methods=["POST"])
def delete():
    """Delete a created team"""
    # Get team id
    id = request.form.get("id")

    # Delete team from database
    db.execute("DELETE FROM cteams WHERE team_id = ?", id)

    return redirect("/created")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return render_template("apology.html", message="Must provide username")

        # Ensure password was submitted
        if not password:
            return render_template("apology.html", message="Must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or rows[0]["password"] != password:
            return render_template("apology.html", message="Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return render_template("index.html")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via render_template)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return render_template("apology.html", message="Must provide username")

        # Ensure password was submitted
        if not password:
            return render_template("apology.html", message="Must provide password")

        if password != confirmation:
            return render_template("apology.html", message="Passwords do not match")

        # Ensure unique username
        users = db.execute("SELECT username FROM users")
        if username in users:
            return render_template("apology.html", message="Username is already taken")

        # Insert new user in database
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, password)

        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("register.html")
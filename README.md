# Soccer Simulator
#### Video Demo: https://youtu.be/VHRviS98P4Q

## Overall Description:
My Final Project for CS50 is a web-based application using JavaScript, Python, SQL, HTML, CSS, and Jinja to simulate soccer matches. All soccer fans looking forward to the day of a match or wondering about the result of a match between two teams that haven't faced each other yet can now simulate the matches and know the results at any time. In addition, it is also possible to create your own team if it is not in the database of any club.
This was a very complex project, but also very fun.

## Code Description:
### - SQLite
The first thing I did for this project was to search for soccer team's databases where I could find their names and overall rating but at the end of the day I found databases with much more data, the raw files are in the 'csvteams' folder.
Then I opened sqlite3 and created the database project.db, and then imported all the three databases that I had downloaded before turning sqlite3 to csv mode with .mode csv. The first was named 'teams.csv' for the European teams, the second 'teamsbr.csv' for Brazilian teams, and lastly 'teamsint' for the international teams.
With this step completed, now I could manipulate my databases more easily and drop all the unuseful columns. What led me to X main columns: Team, Rating, Goals, Pass, Possession, and yellow_cards. Later I noticed that would be interesting to have the main color of the teams crest, so I updated the tables to add the 'color' column, where I inserted a 6-digit hex color code for each team.

### - def index():
Then I started to write the app.py file, imported the flask and cs50 modules, and. Created my first @app.route function def index():

The main page gets all the teams from the database and renders a template to index.html where the structure of the main page would be created.

### - index.html
Created the 'templates' folder and inserted the 'index.html' file. Of course, I did several updates on this page during the process but at the end of the day it has 5 main containers:
- Header: Quick match header
- Display: Team name and team circle with crest color, later I added some javascript to make it more dynamic so that when the user selects the team, its name changes as well as the circle backgroundColor
- Match settings: a select form to choose the team type (European, Brazilian, or International), later I added javascript to update the team options according to this input; a select form to choose the match type (League Match, Cup Match, Friendly Match); a checkbox to enable home advantage
- Select Team: a section with two columns, one for the home team and the other for the away team. Each column has a text input and a select dropdown, the text input filter the dropdown with javascript similar to 'search' from week 9;
- Submit button: submits the form and redirects the user to 'match.html'.

### - def search():
A fetch function called by an EventListener in javascript on 'index.html' to use the input text to update the dropdown options. Get a list of all matching teams using the 'WHERE Team LIKE % __ %' SQL statement and returns it to the template 'search.html'.

### - search.html
This html file uses Jinja syntax to convert the list passed in as an argument to <option'> tags

### - def change():
A function called by an EventListener in javascript that changes all the select options according to the team type value chosen in the match settings

### - change.html
Uses Jinja syntax to convert the list passed in as an argument to <options'> tags

### - base.html
I noticed that a base html layout would be very useful, so I created the 'base.html' file similar to layout.html from finance to create my following html files.

### - def match():
Makes all the error checking to the form submitted on the index page, then gets the information from the two teams on the database rows and converts the values, and uses the random module to make it a bit more dynamic. Finally sends all this information to 'match.html'.

### - match.html
Has a heading, a table with all the match statistics inserted via Jinja, and a 'New Simulation' button to simulate again.

### - def tournament():
The second section of the page. If the request method is GET it renders the 'tournament.html' file, else if the method is post it uses SQLite statements to return 'tournamented.html' and a list with all the teams from the selected tournament as an argument.

### - tournament.html
Simple page with a select dropdown and a submit button

### - tournamented.html
Contains a table with all teams ordered by their respective chances to win the championship

### - def create():
The third section of the page. To create a team you must be logged in so that's why I have the login():, logout(): register(): as well as 'register.html' and 'login.html' files, which are pretty straightforward.

### - create.html
If you're already logged you will see four text input fields each one for a different characteristic of your team (Name, Rating, Possession, Color). After checking possible errors it creates the team and updates the cteams (for created teams) database and redirects you to the last section of the page.

### - def created():
Here you will see a table with the characteristics of all your created teams
as well as an edit column, which you can use to delete the team from the database via the def delete(): function

### - apology.html
This is the template rendered if anything goes wrong. Such as missing input field, wrong value type, not matching passwords, and invalid user/password

### - styles.css
Contains some css code that I used to make the webpage more pretty such as: changing the select tag default display mode, creating the circles to stand for the team crest, changing the background color on hovered sections, change the width of the tables.

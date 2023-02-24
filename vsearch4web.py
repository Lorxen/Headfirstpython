from flask import Flask, render_template, request, session
from search4letters import search4letters

from checker import check_logged_in
from DBcm import UseDataBase


# Initialize flask
app = Flask(__name__)

# Give flask a passw to encrypt cookies
app.secret_key = 'SuperHardPasswordToGuess'


# Add a base configuration to the flask app
app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'vsearchpasswd',
                          'database': 'vsearchlogDB', }


# Do the loggin to get access to the /viewlog and /stadist
@app.route('/login')
def logg_in():
    session['logged_in'] = True
    return 'You are now logged in.'


# Do the loggout to the web
@app.route('/logout')
def logg_out():
    session.pop('logged_in')
    return 'You are now logged out.'


# Log details of the web request and the results
def log_request(req: 'flask_request', res: str) -> None:

    with UseDataBase(app.config['dbconfig']) as cursor:
        _SQL = '''insert into log
                (phrase, letters, ip, browser_string, results)
                values
                (%s,%s,%s,%s,%s)'''
        cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              req.headers.get('User_Agent'),
                              res, ))


# Configure the /search4 with POST method and get the request data
@app.route('/search4', methods=['POST'])
def do_search():
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your results:'
    results = str(search4letters(phrase, letters))
    log_request(request, results)
    return render_template('results.html', the_phrase=phrase, the_letters=letters, the_title=title, the_results=results)


# Configure the default page of the web to go to /enty
@app.route('/')
@app.route('/entry')
def entry_page():
    return render_template('entry.html', the_title='Welcome to search4letters on the web!')


# Configure the /viewlog page to display the database information
@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    with UseDataBase(app.config['dbconfig']) as cursor:
        _SQL = '''select phrase, letters, ip, browser_string, results
                  from log'''
        cursor.execute(_SQL)
        contents = cursor.fetchall()
        titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
        return render_template('viewlog.html',
                               the_title='View Log',
                               the_row_titles=titles,
                               the_data=contents,)


# Configure page to see stadistics of the web
@app.route('/stadist')
@check_logged_in
def stadistics() -> 'html':
    with UseDataBase(app.config['dbconfig']) as cursor:
        details = []
        _SQL = '''select count(*) from log'''
        cursor.execute(_SQL)
        details.append(cursor.fetchall())
        _SQL = '''select count(letters) as 'count', letters
                from log
                group by letters
                order by count desc
                limit 1'''
        cursor.execute(_SQL)
        details[-1].append(cursor.fetchall())
        _SQL = ''' select distinct ip from log'''
        cursor.execute(_SQL)
        details[-1].append(cursor.fetchall())
        _SQL = '''select browser_string, count(browser_string) as 'count'
                from log
                group by browser_string
                order by count desc
                limit 1'''
        cursor.execute(_SQL)
        details[-1].append(cursor.fetchall())

        titles = ('Num Of Requests', 'Most Searched letters', 'Ip', 'Browser')
        return render_template('viewlog.html',
                               the_title='Stadistics',
                               the_row_titles=titles,
                               the_data=tuple(details),)


# Only run in debugg mode if execute from local computer
if __name__ == '__main__':
    app.run(debug=True)

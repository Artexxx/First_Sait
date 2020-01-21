# Веб иллюстратор функции search4letters
# Создаёт страничку с формой, а потом с ответом
from flask import Flask, render_template, request, escape, session
from flask import copy_current_request_context
from vsearch import search4letters

from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError
from checker import check_logged_in

from time import sleep
from threading import Thread

app = Flask(__name__)

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsuser',
                          'password': 'vsearchpasswd',
                          'database': 'vsearch'}


@app.route('/login')
def do_login():
    session['logged_in'] = True
    return "HELLO :)"


@app.route('/logout')
def do_logout():
    session.pop('logged_in')
    return "Bye"


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    """Extract the posted data; perform the search; return results."""

    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        """Log details of the web request and the results."""
        # sleep(15)
        # raise Exception("Something awful just happened.")
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """insert into log
                    (phrase, letters, ip, browser_string, result)
                    values
                    (%s, %s, %s, %s, %s);"""
            cursor.execute(_SQL, (req.form['phrase'],
                                  req.form['letters'],
                                  req.remote_addr,
                                  req.user_agent.browser,
                                  res,))

    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Это твой жалкий результат:'
    results = str(search4letters(phrase, letters))
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print('***** Logging failed with this error:', str(err))
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results, )


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title="Привет собака!")


@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    """Display the contents of the log file as a HTML table."""
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, result
                    from log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()
        titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
        return render_template('viewlog.html',
                               the_title='View Log',
                               the_row_titles=titles,
                               the_data=contents, )
    except ConnectionError as err:
        print('[*]Is your database switched on? Error:', str(err))
    except CredentialsError as err:
        print('[*]User-id/Password issues. Error:', str(err))
    except SQLError as err:
        print('[*]Is your query correct? Error:', str(err))
    except Exception as err:
        print('[*]Something went wrong:', str(err))
    return 'Error'


app.secret_key = 'YouWillNeverGuess'

if __name__ == '__main__':
    app.run(debug=True)

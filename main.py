# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

from contextlib import closing

from lib import db



# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)




def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

#>>> from main import init_db
#>>> init_db()
#>>> exit

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
	g.db = connect_db()
	g.mydb = db.db ()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()



@app.route('/')
def show_entries():
    if not session.get('logged_in'):
	    return render_template('login.html')

    entries = g.mydb.getMyEntries ( session['user_id'])

    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    error = None
    if request.method == 'POST':
		g.db.execute('insert into entries (title, text) values (?, ?)',[request.form['title'], request.form['text']])
		g.db.commit()
		flash('New entry was successfully posted')
		return redirect(url_for('show_entries'))
    return render_template('add_entries.html', error=error)


@app.route('/about')
def about ():
	return render_template('about.html')

@app.route( '/labeler', methods=['GET', 'POST'])
def start_label ():

    if not session.get('logged_in'):
        return render_template('login.html')

    if 'labels' not in session:
        session ['labels'] = g.mydb.getLabels ()

    if request.method == 'POST':
        g.mydb.addLabel (request.form ['data_id'], request.form ['label_id'], session['user_id'])

        if len ( session ['labelentries'] ) == 0:
           flash('No more data')
           return redirect(url_for('show_entries'))
        else:
            id = session ['labelentries'].pop ()
            url = g.mydb.getData ( id )
    else:
        session ['labelentries'] = g.mydb.getIdsSession ()
        if len ( session ['labelentries'] ) == 0:
           flash('No more data')
           return redirect(url_for('show_entries'))
        else:        
            id = session ['labelentries'].pop ()

            url = g.mydb.getData ( id )
    
    return render_template('labeler.html', id=id, url=url, labels=session['labels'])



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':

    	if not ( g.mydb.checkUser (request.form['username'], request.form['password'] )):
    		error = 'Invalid password or Username'
    	else:
    	    session['logged_in'] = True
            session['user_id'] = g.mydb.getUserId (request.form['username'])
    	    return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)




@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))









if __name__ == '__main__':
	app.run()



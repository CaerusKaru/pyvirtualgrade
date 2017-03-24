from flask import Flask, escape, session, request
import os
from . import auth
from . import library
from . import pdf
app = Flask(__name__)
app.register_blueprint(auth.auth_page)
app.register_blueprint(library.library_page)
app.register_blueprint(pdf.pdf_page, url_prefix='/pdf')

@app.errorhandler(auth.NoAuthException)
def no_auth_handler(error):
        return 'invalid credentials', 401

@app.after_request
def post_req(response):
        d = response.get_data()
        d = b")]}',\n" + d
        response.set_data(d)
        return response

@app.route('/')
def index():
        session['username'] = 'aplume01'
        return escape(session['username'])


@app.route('/test')
def test():
        return 'Hello %s' % escape(session['username'])


if __name__ == '__main__':
        app.run(debug=True)

app.secret_key = os.environ['SECRET_KEY']

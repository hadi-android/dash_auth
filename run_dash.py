from dash_test import dash_app
from dash import Dash
import dash_html_components as html
import flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

server = flask.Flask(__name__)

dash_app = Dash(server = server, routes_pathname_prefix='/dashboard/')
dash_app.layout = [html.Div(children='Hello World')]

@server.route("/")
def home():
    return "Hello, Flask!"


@server.route('/dashboard/')
def render_dashboard():
    return flask.redirect('/dash1')

app = DispatcherMiddleware(server, {
    '/dash1': dash_app.server
})

if __name__== "__main__":
     run_simple('0.0.0.0', 8090, app, use_reloader=True, use_debugger=True)


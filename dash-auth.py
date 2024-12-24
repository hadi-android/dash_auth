from flask import Flask, redirect, session, url_for, request
from dash import Dash, html, Input, Output, dcc
from authlib.integrations.flask_client import OAuth
import os

# Flask server setup
server = Flask(__name__)
server.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Auth0 configuration
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_CALLBACK_URL = 'http://127.0.0.1:8050/callback'
AUTH0_LOGOUT_URL = f'https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&returnTo=http://127.0.0.1:8050/'

# Initialize OAuth
oauth = OAuth(server)
auth0 = oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


# Flask routes
@server.route('/')
def home():
    if 'user' in session:
        return redirect('/dash')
    return 'Go to <a href="/login">Login</a> to access the app.'

@server.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)

@server.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    session['user'] = token['userinfo']
    return redirect('/dash')

@server.route('/logout')
def logout():
    session.clear()
    return redirect(AUTH0_LOGOUT_URL)

# Dash app setup
app = Dash(__name__, server=server, url_base_pathname='/dash/')

# Dash layout
app.layout = html.Div([
    html.H1(id='welcome-message'),
    dcc.Location(id='url', refresh=True),
    html.Button('Logout', id='logout-btn', n_clicks=0),
])

# Dash callback to display user info
@app.callback(
    Output('welcome-message', 'children'),
    Input('logout-btn', 'n_clicks'),
)
def update_message(n_clicks):
    if 'user' in session:
        user_info = session['user']
        user_name = user_info.get('name', 'Guest')
        if n_clicks > 0:
            return dcc.Location(href='/logout', id='redirect')
        return f"Welcome, {user_name}!"
    return dcc.Location(href='/login', id='redirect')

# Run the server
if __name__ == '__main__':
    server.run(debug=True, host = '127.0.0.1', port='8050')

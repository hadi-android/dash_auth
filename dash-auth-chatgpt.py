import os
from dash import Dash, html, dcc, Input, Output
from flask import Flask, request, redirect, session, url_for
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode

# load .env file
load_dotenv()
# Flask server
server = Flask(__name__)
server.secret_key = os.getenv("FLASK_SECRET_KEY")

# OAuth setup
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

# Dash app
app = Dash(__name__, server=server, suppress_callback_exceptions=True)
app.title = "Dash with Auth0"

# Layout
# app.layout = html.Div([
#     dcc.Location(id='url', refresh=False),
#     html.Div(id='page-content'),
# ])

# Home Page Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1(id="welcome-message"),
    html.A("Log Out", href="/logout"),
])

# Login Page Layout
login_layout = html.Div([
    html.H1("Login Page"),
    html.A("Log In", href="/login"),
])

# Callbacks
@app.callback(Output('welcome-message', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/callback':
        return handle_callback()
    elif pathname == '/logout':
        return logout()
    elif 'profile' in session:
        return f"Welcome {session.get('profile').get('userinfo').get('name')}"
        
    else:
        return login_layout

def handle_callback():
    token = auth0.authorize_access_token()
    session['profile'] = token
    return redirect('/')

def logout():
    session.clear()
    return redirect(
        "https://" + os.getenv("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("/", _external=True),
                "client_id": os.getenv("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.server.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.server.route("/callback")
def callback():
    return handle_callback()

if __name__ == "__main__":
    app.run_server(debug=True)

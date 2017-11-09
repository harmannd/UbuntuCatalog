from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash
import random
import string

# Imports for database
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# Imports for OAuth login
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:catalog@localhost/catalogdb')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/catalog/JSON')
def catalogJSON():
    """Creates a JSON request view of the catelog categories.

    Returns:
        JSON serialized object of categories.
    """
    catalog = session.query(Category).all()

    return jsonify(Categories=[category.serialize for category in catalog])


@app.route('/catalog/<string:category_name>/JSON')
def catalogItemsJSON(category_name):
    """Creates a JSON request view of the selected catelog category items.

    Returns:
        JSON serialized object of selected category items.
    """
    selected_category = session.query(Category).filter_by(
        name=category_name).one()
    items = session.query(Item).filter_by(category=selected_category).all()

    return jsonify(Items=[item.serialize for item in items])


@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def catalogItemJSON(category_name, item_name):
    """Creates a JSON request view of the selected catelog category item.

    Returns:
        JSON serialized object of selected item.
    """
    selected_category = session.query(Category).filter_by(
        name=category_name).one()
    selected_item = session.query(Item).filter_by(
        category=selected_category, name=item_name).one()

    return jsonify(selected_item.serialize)


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    """Displays the home page with the current categories and latest items.

    Returns:
        Public catelog template: if no user is logged in.
        Catelog template: if a user is logged in.
    """
    categories = session.query(Category).all()
    latestItems = session.query(Item).limit(10)
    if 'username' not in login_session:
        return render_template(
            'public_catalog.html',
            categories=categories,
            latestItems=latestItems
        )
    else:
        return render_template(
            'catalog.html',
            categories=categories,
            latestItems=latestItems
        )


@app.route('/catalog/<string:category_name>/')
def showCategoryItems(category_name):
    """Displays the current categories and the selected category's items.

    Args:
        category_name (str): Name of the selected category.

    Returns:
        Public category items template: if no user is logged in.
        Category items template: if a user is logged in.
    """
    categories = session.query(Category).all()
    selected_category = session.query(Category).filter_by(
        name=category_name).one()
    items = session.query(Item).filter_by(category=selected_category).all()

    if 'username' not in login_session:
        return render_template(
            'public_category_items.html',
            categories=categories,
            items=items,
            category_name=category_name
        )
    else:
        return render_template(
            'category_items.html',
            categories=categories,
            items=items,
            category_name=category_name
        )


@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showItem(category_name, item_name):
    """Displays the selected item's details.

    Args:
        category_name (str): Name of the selected category.
        item_name (str): Name of the selected item.

    Returns:
        Public item template: if no user is logged in.
        Item template: if a user is logged in.
    """
    item_category = session.query(Category).filter_by(
        name=category_name).one()
    item = session.query(Item).filter_by(
        name=item_name, category=item_category).one()

    if 'username' not in login_session:
        return render_template('public_item.html', item=item)
    else:
        return render_template('item.html', item=item)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    """Allows user to create a new item.

    Returns:
        Redirect to Login page: if no user is logged in.
        GET: New item template.
        POST: Success: Redirect to home page.
              Failure: New item template with error message.
    """
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    categories = session.query(Category).all()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        image_url = request.form['image_url']

        if name and description:
            newItem = Item(
                name=name,
                description=description,
                image_url=image_url,
                category=category,
                user_id=login_session['user_id']
            )

            session.add(newItem)
            session.commit()

            return redirect(url_for('showCatalog'))
        else:
            return render_template(
                'new_item.html',
                categories=categories,
                error="Name and description please!"
            )
    else:
        return render_template('new_item.html', categories=categories)


@app.route(
    '/catalog/<string:category_name>/<string:item_name>/edit/',
    methods=['GET', 'POST']
)
def editItem(category_name, item_name):
    """Allows user to edit selected item's information.

    Args:
        category_name (str): Name of the selected category.
        item_name (str): Name of the selected item.

    Returns:
        Redirect to Login page: if no user is logged in.
        Redirect to home page: if user is not item's creator.
        GET: Edit item template.
        POST: Success: Redirect to home page.
              Failure: Edit item template with error message.
    """
    if 'username' not in login_session:
        flash("Please login before editing items.")
        return redirect(url_for('showLogin'))
    categories = session.query(Category).all()
    item_category = session.query(Category).filter_by(
        name=category_name).one()
    itemToEdit = session.query(Item).filter_by(
        name=item_name, category=item_category).one()

    if login_session['user_id'] != itemToEdit.user_id:
        flash("You can't edit that item.")
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image_url = request.form['image_url']
        category = session.query(Category).filter_by(
            name=request.form['category']).one()

        if name and description:
            itemToEdit.name = name
            itemToEdit.description = description
            itemToEdit.category = category
            itemToEdit.image_url = image_url

            session.add(itemToEdit)
            session.commit()

            flash("Item edited successfully!")
            return redirect(url_for('showCatalog'))
        else:
            return render_template(
                'edit_Item.html',
                categories=categories,
                item=itemToEdit,
                category_name=item_category.name,
                error="Name and description please!"
            )
    else:
        return render_template(
            'edit_item.html',
            categories=categories,
            item=itemToEdit,
            category_name=item_category.name
        )


@app.route(
    '/catalog/<string:category_name>/<string:item_name>/delete/',
    methods=['GET', 'POST']
)
def deleteItem(category_name, item_name):
    """Allows user to delete selected item.

    Args:
        category_name (str): Name of the selected category.
        item_name (str): Name of the selected item.

    Returns:
        Redirect to Login page: if no user is logged in.
        Redirect to home page: if user is not item's creator.
        GET: Delete item template.
        POST: Success: Redirect to home page.
    """
    if 'username' not in login_session:
        flash("Please login before deleteing items.")
        return redirect(url_for('showLogin'))
    item_category = session.query(Category).filter_by(
        name=category_name).one()
    itemToDelete = session.query(Item).filter_by(
        name=item_name, category=item_category).one()

    if login_session['user_id'] != itemToDelete.user_id:
        flash("You can't delete that item.")
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()

        flash("Item deleted successfully!")
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'delete_item.html',
            item=itemToDelete,
            category_name=item_category.name
        )


@app.route('/login')
def showLogin():
    """Create anti-forgery state token.

    Returns:
        Login template.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


def createUser(login_session):
    """Creates a new database user with login session information.

    Args:
        login_session (session): Stores 3rd party login information.

    Returns:
        New user's id.
    """
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()

    return user.id


def getUserInfo(user_id):
    """Gets database User object.

    Args:
        user_id (int): User's id.

    Returns:
        User with given id.
    """
    user = session.query(User).filter_by(id=user_id).one()

    return user


def getUserID(email):
    """Gets user id by using given email.

    Args:
        email (str): User's email.

    Returns:
        User id: if user with given email exists.
        None: otherwise.
    """
    try:
        user = session.query(User).filter_by(email=email).one()

        return user.id
    except:
        return None


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Attempts to log in the user by using Google login.

    Returns:
        Json error response: if something goes wrong.
        login success message with login information: otherwise.
    """
    # Validate state token.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response
    # Obtain authorization code.
    code = request.data
    # Upgrade the authorization code into a credentials object.
    app_path = '/var/www/ubuntuCatalog/ubuntuCatalog/g_client_secrets.json'
    try:
	oauth_flow = flow_from_clientsecrets(app_path, scope='')
	oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

        return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'

        return response
    # Verify that the access token is valid for this app.
    client_id = json.loads(open(app_path, 'r').read())['web']['client_id']
    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'

        return response
    # Check if current user is already connected.
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Check if user exists.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Create login success message with login information.
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Revoke a current user's token and reset their login_session.

    Returns:
        Json error response: if something goes wrong.
    """
    access_token = login_session['access_token']

    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'

        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Attempts to log in the user by using Facebook login.

    Returns:
        Json error response: if something goes wrong.
        login success message with login information: otherwise.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response
    access_token = request.data
    print "access token received %s " % access_token

    # Exchange client token for long-lived server-side token with GET.
    app_path = '/var/www/ubuntuCatalog/ubuntuCatalog/fb_client_secrets.json'
    app_id = json.loads(
        open(app_path, 'r').read())['web']['app_id']
    app_secret = json.loads(
        open(app_path, 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.9/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    token = 'access_token=' + data['access_token']

    # Use token to get user info from API make API call with new token.
    url = 'https://graph.facebook.com/v2.9/me?%s&fields=name,id,email,picture' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['picture'] = data['picture']["data"]["url"]
    login_session['access_token'] = access_token

    # Check if user exists.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Create login success message with login information.
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1><img src="'
    output += login_session['picture']
    output += ' ">'

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """Delete current user's access token and login id.

    Returns:
        Logout success message.
    """
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    return "You have been logged out"


@app.route('/disconnect')
def disconnect():
    """Disconnect based on provider, logging out the user.

    Returns:
        Redirect to homepage with status message.
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run()

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import User, get_user_by_id, get_user_by_email
from fraud_detector import ImageFraudDetector
import os
from config import Config
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize the fraud detector
detector = ImageFraudDetector()

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

def get_google_provider_cfg():
    try:
        response = requests.get(app.config['GOOGLE_DISCOVERY_URL'])
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get Google provider config: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember-me') else False
        
        user = get_user_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Please check your login details and try again.')
    
    return render_template('login.html')

@app.route('/login/google')
def google_login():
    logger.info("Starting Google login process")
    
    # Get Google provider configuration
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        flash("Error connecting to Google's servers")
        return redirect(url_for('login'))
    
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    # Construct the redirect URI explicitly
    redirect_uri = 'http://127.0.0.1:5000/login/google/callback'
    
    logger.info(f"Using redirect URI: {redirect_uri}")
    
    # Prepare the request URI for Google's OAuth 2.0 server
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )
    
    logger.info(f"Redirecting to Google authorization: {request_uri}")
    return redirect(request_uri)

@app.route('/login/google/callback')
def google_callback():
    logger.info("Received Google callback")
    
    try:
        # Get authorization code from Google
        code = request.args.get("code")
        if not code:
            logger.error("No authorization code received from Google")
            flash("Authentication failed: No authorization code received")
            return redirect(url_for('login'))
        
        # Get Google provider configuration
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            flash("Error connecting to Google's servers")
            return redirect(url_for('login'))
        
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Use the same redirect URI as in the authorization request
        redirect_uri = 'http://127.0.0.1:5000/login/google/callback'
        
        logger.info(f"Using callback redirect URI: {redirect_uri}")
        
        # Prepare and send token request
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=redirect_uri,
            code=code
        )
        
        logger.debug(f"Sending token request to: {token_url}")
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(app.config['GOOGLE_CLIENT_ID'], app.config['GOOGLE_CLIENT_SECRET']),
        )

        # Parse the token response
        client.parse_request_body_response(token_response.text)
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        logger.debug("Received user info from Google")
        
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            users_name = userinfo_response.json().get("given_name", users_email.split('@')[0])
            
            # Get or create user
            user = get_user_by_email(users_email)
            if not user:
                logger.info(f"Creating new user for {users_email}")
                user = User.create(
                    username=users_name,
                    email=users_email,
                    password_hash=generate_password_hash(os.urandom(24).hex())
                )
            
            # Log in user
            login_user(user)
            logger.info(f"Successfully logged in user: {users_email}")
            return redirect(url_for('dashboard'))
        else:
            logger.warning("Google authentication failed: Email not verified")
            flash("Google authentication failed: Email not verified")
            return redirect(url_for('login'))
            
    except Exception as e:
        logger.error(f"Google authentication error: {str(e)}", exc_info=True)
        flash(f"Failed to log in with Google: {str(e)}")
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if get_user_by_email(email):
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        user = User.create(username, email, password)
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Analyze the image
            result = detector.analyze(filepath)
            
            # Add clear verdict message
            score = result.get('authenticity_score', 0)
            if score >= 0.7:
                result['verdict'] = 'This image appears to be authentic'
            elif score >= 0.4:
                result['verdict'] = 'This image shows some signs of manipulation'
            else:
                result['verdict'] = 'This image appears to be fraudulent'
            
            # Save scan to user's history
            current_user.add_scan(filename, result)
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            return jsonify(result)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)

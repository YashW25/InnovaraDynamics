import os
import sqlite3
import secrets
import re
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
import markdown
from bleach import clean
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'innovara#asdfghjkl@12345678')

# EmailJS configuration - OTP
EMAILJS_TEMPLATE_ID = os.environ.get('EMAILJS_TEMPLATE_ID', 'template_dadxpbx')
EMAILJS_SERVICE_ID = os.environ.get('EMAILJS_SERVICE_ID', 'service_c7vxyss')
EMAILJS_PUBLIC_KEY = os.environ.get('EMAILJS_PUBLIC_KEY', 'zC_dJUm7lVsQy8e8R')
EMAILJS_ACCESS_TOKEN = os.environ.get('EMAILJS_ACCESS_TOKEN', 'dJsjM4gogCVKPk1T65HN9')

# EmailJS configuration - Contact Form
CONTACT_TEMPLATE_ID = os.environ.get('CONTACT_TEMPLATE_ID', 'template_yqype79')

# Contact email
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'innovaradynamics@gmail.com')

# Database configuration
DATABASE = os.path.join(os.path.dirname(__file__), 'data', 'posts.db')

def init_db():
    """Initialize the database if it doesn't exist"""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Existing posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            excerpt TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # New team members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            about TEXT NOT NULL,
            image_url TEXT,
            portfolio_link TEXT,
            linkedin_link TEXT,
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    
    # New projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            company_name TEXT NOT NULL,
            about TEXT NOT NULL,
            project_link TEXT,
            company_link TEXT,
            image_url TEXT,
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def generate_slug(title):
    """Generate URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def generate_excerpt(content, max_length=150):
    """Generate excerpt from content"""
    # Remove markdown formatting for excerpt
    text = re.sub(r'[#*`\[\]()]', '', content)
    text = ' '.join(text.split())
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...'

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/services')
def services():
    """Services page"""
    return render_template('services.html')

@app.route('/about')
def about():
    """About page with dynamic team members and projects"""
    db = get_db()
    
    # Get active team members
    team_members = db.execute('''
        SELECT * FROM team_members 
        WHERE is_active = 1 
        ORDER BY display_order, name
    ''').fetchall()
    
    # Get active projects
    projects = db.execute('''
        SELECT * FROM projects 
        WHERE is_active = 1 
        ORDER BY display_order, created_at DESC
    ''').fetchall()
    
    return render_template('about.html', team_members=team_members, projects=projects)

@app.route('/partner', methods=['GET', 'POST'])
def partner():
    """Partner page with contact form"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validate form data
        if not name or not email or not message:
            flash('Please fill in all required fields.', 'danger')
            return render_template('partner.html', name=name, email=email, message=message)
        
        # Send email using EmailJS
        try:
            # Get current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            emailjs_url = "https://api.emailjs.com/api/v1.0/email/send"
            emailjs_data = {
                "service_id": EMAILJS_SERVICE_ID,
                "template_id": CONTACT_TEMPLATE_ID,
                "user_id": EMAILJS_PUBLIC_KEY,
                "template_params": {
                    "name": name,
                    "email": email,
                    "message": message,
                    "timestamp": timestamp,
                    "to_email": CONTACT_EMAIL
                }
            }
            
            response = requests.post(emailjs_url, json=emailjs_data, timeout=10)
            
            if response.status_code == 200:
                flash('Thank you for your interest! We have received your message and will get back to you soon.', 'success')
                
                # Log the successful submission
                print(f"Contact form submitted: {name} ({email}) at {timestamp}")
                
            else:
                flash('Thank you for your interest! Your message has been received. We will get back to you soon.', 'success')
                print(f"EmailJS response error: {response.status_code} - {response.text}")
                
        except Exception as e:
            # Even if email fails, show success to user but log the error
            flash('Thank you for your interest! We have received your message and will get back to you soon.', 'success')
            print(f"Error sending email: {str(e)}")
        
        return redirect(url_for('partner'))
    
    return render_template('partner.html')

@app.route('/blog')
def blog_list():
    """List all blog posts"""
    db = get_db()
    posts = db.execute('''
        SELECT id, title, slug, excerpt, created_at 
        FROM posts 
        ORDER BY created_at DESC
    ''').fetchall()
    return render_template('blog_list.html', posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    """Display a single blog post"""
    db = get_db()
    post = db.execute('''
        SELECT id, title, slug, excerpt, content, created_at 
        FROM posts 
        WHERE slug = ?
    ''', (slug,)).fetchone()
    
    if post is None:
        flash('Post not found.', 'danger')
        return redirect(url_for('blog_list'))
    
    # Convert markdown to HTML
    html_content = markdown.markdown(post['content'])
    # Sanitize HTML
    html_content = clean(html_content, tags=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                             'strong', 'em', 'ul', 'ol', 'li', 'a', 'code', 
                                             'pre', 'blockquote', 'br', 'hr', 'img'],
                        attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title']})
    
    return render_template('blog_post.html', post=post, content=html_content)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page with OTP system"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        email = request.form.get('email', '')
        otp = request.form.get('otp', '')
        
        # Check if this is OTP verification step
        if 'otp_sent' in session and session.get('otp_sent'):
            # Verify OTP
            if otp == session.get('otp_code') and username == ADMIN_USERNAME:
                session['admin_logged_in'] = True
                session.pop('otp_sent', None)
                session.pop('otp_code', None)
                flash('Login successful!', 'success')
                return redirect(url_for('admin_create'))
            else:
                flash('Invalid OTP. Please try again.', 'danger')
                return render_template('admin_login.html', show_otp=True, username=username, email=email)
        
        # Initial login attempt - verify credentials and send OTP
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            if not email:
                flash('Please provide your email for OTP verification.', 'warning')
                return render_template('admin_login.html', username=username)
            
            # Generate OTP
            otp_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            session['otp_code'] = otp_code
            session['otp_sent'] = True
            
            # Send OTP via EmailJS
            try:
                emailjs_url = f"https://api.emailjs.com/api/v1.0/email/send"
                emailjs_data = {
                    "service_id": EMAILJS_SERVICE_ID,
                    "template_id": EMAILJS_TEMPLATE_ID,
                    "user_id": EMAILJS_PUBLIC_KEY,
                    "accessToken": EMAILJS_ACCESS_TOKEN,
                    "template_params": {
                        "to_email": email,
                        "otp_code": otp_code,
                        "user_name": username
                    }
                }
                response = requests.post(emailjs_url, json=emailjs_data, timeout=10)
                if response.status_code == 200:
                    flash('OTP sent to your email. Please check and enter the code.', 'success')
                    return render_template('admin_login.html', show_otp=True, username=username, email=email)
                else:
                    flash('Failed to send OTP. Please try again.', 'danger')
            except Exception as e:
                flash(f'Error sending OTP: {str(e)}. Please try again.', 'danger')
            
            return render_template('admin_login.html', username=username, email=email)
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('otp_sent', None)
    session.pop('otp_code', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/create', methods=['GET', 'POST'])
@admin_required
def admin_create():
    """Create new blog post (admin only)"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            flash('Title and content are required.', 'danger')
            return render_template('admin_create.html')
        
        slug = generate_slug(title)
        excerpt = generate_excerpt(content)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        db = get_db()
        try:
            db.execute('''
                INSERT INTO posts (title, slug, excerpt, content, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, slug, excerpt, content, created_at))
            db.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('blog_post', slug=slug))
        except sqlite3.IntegrityError:
            flash('A post with this title already exists. Please use a different title.', 'danger')
            return render_template('admin_create.html', title=title, content=content)
        except Exception as e:
            flash(f'Error creating post: {str(e)}', 'danger')
            return render_template('admin_create.html', title=title, content=content)
    
    return render_template('admin_create.html')

@app.route('/admin/team', methods=['GET', 'POST'])
@admin_required
def admin_team():
    """Admin panel for managing team members"""
    db = get_db()
    
    if request.method == 'POST':
        if 'delete_id' in request.form:
            # Delete team member
            member_id = request.form['delete_id']
            db.execute('DELETE FROM team_members WHERE id = ?', (member_id,))
            db.commit()
            flash('Team member deleted successfully!', 'success')
        else:
            # Add or update team member
            name = request.form.get('name', '').strip()
            position = request.form.get('position', '').strip()
            about = request.form.get('about', '').strip()
            portfolio_link = request.form.get('portfolio_link', '').strip()
            linkedin_link = request.form.get('linkedin_link', '').strip()
            display_order = request.form.get('display_order', 0)
            
            if not name or not position or not about:
                flash('Name, position, and about are required.', 'danger')
                return redirect(url_for('admin_team'))
            
            member_id = request.form.get('id')
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if member_id:  # Update existing
                db.execute('''
                    UPDATE team_members 
                    SET name=?, position=?, about=?, portfolio_link=?, linkedin_link=?, display_order=?
                    WHERE id=?
                ''', (name, position, about, portfolio_link, linkedin_link, display_order, member_id))
                flash('Team member updated successfully!', 'success')
            else:  # Add new
                db.execute('''
                    INSERT INTO team_members (name, position, about, portfolio_link, linkedin_link, display_order, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, position, about, portfolio_link, linkedin_link, display_order, created_at))
                flash('Team member added successfully!', 'success')
            
            db.commit()
        
        return redirect(url_for('admin_team'))
    
    # GET request - show all team members
    team_members = db.execute('''
        SELECT * FROM team_members 
        WHERE is_active = 1 
        ORDER BY display_order, name
    ''').fetchall()
    
    return render_template('admin_team.html', team_members=team_members)

@app.route('/admin/projects', methods=['GET', 'POST'])
@admin_required
def admin_projects():
    """Admin panel for managing projects"""
    db = get_db()
    
    if request.method == 'POST':
        if 'delete_id' in request.form:
            # Delete project
            project_id = request.form['delete_id']
            db.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            db.commit()
            flash('Project deleted successfully!', 'success')
        else:
            # Add or update project
            project_name = request.form.get('project_name', '').strip()
            company_name = request.form.get('company_name', '').strip()
            about = request.form.get('about', '').strip()
            project_link = request.form.get('project_link', '').strip()
            company_link = request.form.get('company_link', '').strip()
            display_order = request.form.get('display_order', 0)
            
            if not project_name or not company_name or not about:
                flash('Project name, company name, and about are required.', 'danger')
                return redirect(url_for('admin_projects'))
            
            project_id = request.form.get('id')
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if project_id:  # Update existing
                db.execute('''
                    UPDATE projects 
                    SET project_name=?, company_name=?, about=?, project_link=?, company_link=?, display_order=?
                    WHERE id=?
                ''', (project_name, company_name, about, project_link, company_link, display_order, project_id))
                flash('Project updated successfully!', 'success')
            else:  # Add new
                db.execute('''
                    INSERT INTO projects (project_name, company_name, about, project_link, company_link, display_order, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (project_name, company_name, about, project_link, company_link, display_order, created_at))
                flash('Project added successfully!', 'success')
            
            db.commit()
        
        return redirect(url_for('admin_projects'))
    
    # GET request - show all projects
    projects = db.execute('''
        SELECT * FROM projects 
        WHERE is_active = 1 
        ORDER BY display_order, created_at DESC
    ''').fetchall()
    
    return render_template('admin_projects.html', projects=projects)

if __name__ == '__main__':
    init_db()
    app.run(debug=os.environ.get('FLASK_ENV') == 'development', host='0.0.0.0', port=5000)
# Innovara Dynamics Website

A complete production-grade web application for Innovara Dynamics featuring a Flask backend, Bootstrap 5 frontend, light/dark theme toggle, SQLite blog system, admin authentication with OTP, and full CMS capabilities.

## Features

- ✨ **Modern UI**: Bootstrap 5 responsive design
- 🌓 **Theme System**: Light/Dark mode toggle with CSS variables
- 📝 **Blog System**: Full-featured blog with Markdown support
- 🔐 **Admin Authentication**: Secure login with EmailJS OTP verification
- 💼 **CMS**: Rich text editor for creating blog posts
- 🐳 **Docker Ready**: Docker configuration for easy deployment
- 📱 **Fully Responsive**: Mobile-first design

## Installation

1. **Clone or download the repository**

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Running the Application

1. **Start the Flask server**:
```bash
python app.py
```

2. **Open your browser** and navigate to:
```
http://localhost:5000
```

The database will be automatically created in the `data/` directory on first run.

## Admin Login

**Username:** `admin`  
**Password:** `innovara#asdfghjkl@12345678`

### OTP System

The admin login uses a two-factor authentication system:
1. Enter username, password, and email
2. An OTP (One-Time Password) will be sent to your email via EmailJS
3. Enter the 6-digit OTP to complete login

**EmailJS Configuration:**
- Template ID: `template_dadxpbx`
- Service ID: `service_c7vxyss`
- Public Key: `zC_dJUm7lVsQy8e8R`
- Access Token: `dJsjM4gogCVKPk1T65HN9`

## Creating Blog Posts

1. **Login as admin** (see Admin Login section above)
2. Navigate to **Admin** in the navbar (or `/admin/create`)
3. Fill in the blog post:
   - **Title**: Will auto-generate a URL-friendly slug
   - **Content**: Use Markdown syntax (supports rich text editor)
4. Click **Publish Post**

### Markdown Support

The blog system supports full Markdown syntax including:
- Headers (# ## ###)
- Bold (**text**) and italic (*text*)
- Lists (ordered and unordered)
- Links and images
- Code blocks
- Blockquotes

The excerpt will be auto-generated from the content (first 150 characters).

## Theme Toggle

The application features a light/dark theme system:

### Light Theme
- Primary: Light Blue (#3B82F6)
- Background: White (#FFFFFF)
- Text: Dark (#0F172A)

### Dark Theme
- Primary: Dark Blue (#1E3A8A)
- Background: Black (#000000)
- Text: Light (#E2E8F0)

### How It Works

1. Click the theme toggle button (☀/🌙) in the navbar
2. The theme preference is saved to `localStorage`
3. The `.dark-mode` class is added/removed from the `<html>` element
4. All colors are controlled by CSS variables for smooth transitions

The theme selection persists across page reloads.

## Project Structure

```
innovara-website/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── Dockerfile            # Docker configuration
├── .dockerignore         # Docker ignore file
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet with theme system
│   ├── js/
│   │   └── main.js       # Theme toggle JavaScript
│   └── img/              # Image assets
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── services.html     # Services page
│   ├── about.html        # About page
│   ├── partner.html      # Partner page
│   ├── blog_list.html    # Blog listing
│   ├── blog_post.html    # Single blog post
│   ├── admin_login.html  # Admin login
│   └── admin_create.html # Create blog post
└── data/
    └── posts.db          # SQLite database (auto-created)
```

## Deployment

### Docker Deployment

1. **Build the Docker image**:
```bash
docker build -t innovara-website .
```

2. **Run the container**:
```bash
docker run -p 5000:5000 innovara-website
```

### Deploy on Render

1. Connect your repository to Render
2. Create a new **Web Service**
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Python Version**: 3.11+
4. Add environment variable:
   - `SECRET_KEY`: Generate a secure random key

### Deploy on Railway

1. Connect your repository to Railway
2. Railway will auto-detect Python
3. Set environment variables:
   - `SECRET_KEY`: Generate a secure random key
4. Deploy!

**Note:** For production, use `gunicorn` or similar WSGI server:
```bash
pip install gunicorn
gunicorn app:app
```

## Environment Variables

- `SECRET_KEY`: Flask secret key for session management (auto-generated if not set)

## Database

The application uses SQLite stored in `data/posts.db`. The database is automatically created on first run with the following schema:

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    excerpt TEXT,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## License

© 2024 Innovara Dynamics. All rights reserved.

## Support

For issues or questions, please contact: contact@innovaradynamics.com


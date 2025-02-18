#!/usr/bin/env python
import os
import json
import datetime
from main import app, db
from models import User, Blog, Book, SocialLink, Site

# Set DATA_DIR to point to the frontend/data directory relative to the project root.
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'data')
# Set PARTIALS_DIR to point to the frontend/partials directory.
PARTIALS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'partials')

def generate_slug(username):
    """Simple slug generator from username."""
    return username.lower().replace(" ", "-")

def seed_auth():
    """Seed the User table from auth.json."""
    auth_path = os.path.join(DATA_DIR, 'auth.json')
    print("Looking for auth.json at:", auth_path)
    if os.path.exists(auth_path):
        with open(auth_path, 'r') as f:
            auth_data = json.load(f)
        # Only seed if no user exists
        if User.query.first() is None:
            slug = auth_data.get('slug') or generate_slug(auth_data.get('username', ''))
            user = User(
                username=auth_data.get('username', ''),
                email=auth_data.get('email', ''),
                name=auth_data.get('name', ''),
                slug=slug
            )
            if auth_data.get('passwordHash'):
                user.password_hash = auth_data.get('passwordHash')
            else:
                print("Warning: No passwordHash provided in auth.json.")

            # Load the author partial (about the author)
            author_partials_path = os.path.join(PARTIALS_DIR, 'author.html')
            print("Looking for author.html at:", author_partials_path)
            if os.path.exists(author_partials_path):
                with open(author_partials_path, 'r') as f:
                    user.about = f.read()
            else:
                print("author.html not found in partials.")

            # Load philosophy partial
            philosophy_partials_path = os.path.join(PARTIALS_DIR, 'philosophy.html')
            print("Looking for philosophy.html at:", philosophy_partials_path)
            if os.path.exists(philosophy_partials_path):
                with open(philosophy_partials_path, 'r') as f:
                    user.philosophy = f.read()
            else:
                print("philosophy.html not found in partials.")

            db.session.add(user)
            db.session.commit()
            print("Seeded auth.json into User table.")
        else:
            print("User table already has data; skipping auth seed.")
    else:
        print("auth.json file not found.")

def seed_blogs():
    """Seed the Blog table from blog.json."""
    blogs_path = os.path.join(DATA_DIR, 'blog.json')
    print("Looking for blog.json at:", blogs_path)
    if os.path.exists(blogs_path):
        with open(blogs_path, 'r') as f:
            blogs_data = json.load(f)
        if Blog.query.count() == 0:
            author = User.query.first()
            if not author:
                print("No author found; cannot seed blogs.")
                return
            for blog in blogs_data:
                publish_date_str = blog.get('publish_date')
                if publish_date_str:
                    try:
                        publish_date = datetime.datetime.strptime(publish_date_str, '%Y-%m-%d').date()
                    except Exception:
                        publish_date = datetime.date.today()
                else:
                    publish_date = datetime.date.today()

                # Load HTML content for the blog if provided.
                html_file = blog.get('html', '')
                html_content = None
                if html_file:
                    full_html_path = os.path.join(PARTIALS_DIR, os.path.basename(html_file))
                    print("Looking for blog partial at:", full_html_path)
                    if os.path.exists(full_html_path):
                        with open(full_html_path, 'r') as hf:
                            html_content = hf.read()
                    else:
                        print(f"HTML file {full_html_path} not found.")

                new_blog = Blog(
                    title=blog.get('title', ''),
                    subtitle=blog.get('subtitle', ''),
                    description=blog.get('description', ''),
                    image=blog.get('image', ''),
                    html_content=html_content,
                    published=blog.get('published', True),
                    name=blog.get('name', ''),
                    publish_date=publish_date,
                    show=blog.get('show', True),
                    author_id=author.id
                )
                db.session.add(new_blog)
            db.session.commit()
            print("Seeded blog.json into Blog table.")
        else:
            print("Blog table already seeded; skipping blogs seed.")
    else:
        print("blog.json file not found.")

def seed_books():
    """Seed the Book table from books.json."""
    books_path = os.path.join(DATA_DIR, 'books.json')
    print("Looking for books.json at:", books_path)
    if os.path.exists(books_path):
        with open(books_path, 'r') as f:
            books_data = json.load(f)
        if Book.query.count() == 0:
            author = User.query.first()
            if not author:
                print("No author found; cannot seed books.")
                return
            for book in books_data:
                new_book = Book(
                    title=book.get('title', ''),
                    description=book.get('description', ''),
                    image=book.get('image', ''),
                    published=book.get('published', False),
                    amazonUrl=book.get('amazonUrl', ''),
                    barnesandnobleUrl=book.get('barnesandnobleUrl', ''),
                    googlebooksUrl=book.get('googlebooksUrl', ''),
                    author_id=author.id
                )
                db.session.add(new_book)
            db.session.commit()
            print("Seeded books.json into Book table.")
        else:
            print("Book table already seeded; skipping books seed.")
    else:
        print("books.json file not found.")

def seed_site():
    """Seed the Site table from site.json."""
    site_path = os.path.join(DATA_DIR, 'site.json')
    print("Looking for site.json at:", site_path)
    if os.path.exists(site_path):
        with open(site_path, 'r') as f:
            site_data = json.load(f)
        if Site.query.count() == 0:
            author = User.query.first()
            if not author:
                print("No author found; cannot seed site settings.")
                return
            new_site = Site(
                title=site_data.get('title', ''),
                author=site_data.get('author', ''),
                introduction=site_data.get('introduction', ''),
                navbar=site_data.get('colorPalette', {}).get('navbar', ''),
                footer=site_data.get('colorPalette', {}).get('footer', ''),
                heroBackground=site_data.get('colorPalette', {}).get('heroBackground', ''),
                user_id=author.id
            )
            db.session.add(new_site)
            db.session.commit()
            print("Seeded site.json into Site table.")
        else:
            print("Site table already seeded; skipping site seed.")
    else:
        print("site.json file not found.")

def seed_social():
    """Seed the SocialLink table from social.json."""
    social_path = os.path.join(DATA_DIR, 'social.json')
    print("Looking for social.json at:", social_path)
    if os.path.exists(social_path):
        with open(social_path, 'r') as f:
            social_data = json.load(f)
        if SocialLink.query.count() == 0:
            author = User.query.first()
            for social in social_data:
                new_social = SocialLink(
                    name=social.get('name', ''),
                    url=social.get('url', ''),
                    icon=social.get('icon', ''),
                    color=social.get('color', ''),
                    user_id=author.id if author else None
                )
                db.session.add(new_social)
            db.session.commit()
            print("Seeded social.json into SocialLink table.")
        else:
            print("SocialLink table already seeded; skipping social seed.")
    else:
        print("social.json file not found.")

if __name__ == '__main__':
    with app.app_context():
        seed_auth()
        seed_blogs()
        seed_books()
        seed_site()
        seed_social()

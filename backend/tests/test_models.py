import datetime
import pytest
from app import app, db
from models import User, Rating, Configuration, Blog, Book, SocialLink, Site


def test_user_password():
    """Test that setting and checking a password works correctly."""
    user = User(username="testuser", email="test@example.com", name="Test User", slug="test-user")
    user.set_password("mypassword")
    assert user.check_password("mypassword") is True
    assert user.check_password("wrongpassword") is False


def test_configuration_model():
    """Test creation and retrieval of a configuration record."""
    config = Configuration(config_key="site_title", config_value="Test Site")
    db.session.add(config)
    db.session.commit()
    retrieved = Configuration.query.filter_by(config_key="site_title").first()
    assert retrieved is not None
    assert retrieved.config_value == "Test Site"


def test_blog_model():
    """Test creation of a blog post and default publish_date."""
    # Create an author for foreign key association
    user = User(username="blogger", email="blogger@example.com", name="Blogger", slug="blogger")
    user.set_password("secret")
    db.session.add(user)
    db.session.commit()

    # Create a blog post without specifying publish_date
    blog = Blog(
        title="Test Blog",
        subtitle="Testing",
        description="This is a test blog.",
        image="test.jpg",
        published=True,
        name="test-blog",
        show=True,
        author_id=user.id
    )
    db.session.add(blog)
    db.session.commit()

    retrieved = Blog.query.filter_by(name="test-blog").first()
    assert retrieved is not None
    # Check that publish_date defaults to today's date
    assert retrieved.publish_date == datetime.date.today()
    assert retrieved.show is True


def test_book_model():
    """Test creation of a book record with extra URL fields."""
    # Create an author for foreign key association
    user = User(username="bookauthor", email="bookauthor@example.com", name="Book Author", slug="bookauthor")
    user.set_password("secret")
    db.session.add(user)
    db.session.commit()

    book = Book(
        title="Test Book",
        description="A book for testing.",
        image="book.jpg",
        published=True,
        amazonUrl="http://amazon.com/test-book",
        barnesandnobleUrl="http://barnesandnoble.com/test-book",
        googlebooksUrl="http://googlebooks.com/test-book",
        author_id=user.id
    )
    db.session.add(book)
    db.session.commit()

    retrieved = Book.query.filter_by(title="Test Book").first()
    assert retrieved is not None
    assert retrieved.amazonUrl == "http://amazon.com/test-book"
    assert retrieved.barnesandnobleUrl == "http://barnesandnoble.com/test-book"
    assert retrieved.googlebooksUrl == "http://googlebooks.com/test-book"


def test_social_link_model():
    """Test creation of a social link record."""
    # Create an author for foreign key association
    user = User(username="socialuser", email="social@example.com", name="Social User", slug="socialuser")
    user.set_password("secret")
    db.session.add(user)
    db.session.commit()

    social = SocialLink(
        name="Facebook",
        url="http://facebook.com/test",
        icon="fb.svg",
        color="blue darken-4",
        user_id=user.id
    )
    db.session.add(social)
    db.session.commit()

    retrieved = SocialLink.query.filter_by(name="Facebook").first()
    assert retrieved is not None
    assert retrieved.url == "http://facebook.com/test"


def test_site_model():
    """Test creation of site settings for an author."""
    # Create an author for foreign key association
    user = User(username="siteuser", email="site@example.com", name="Site User", slug="siteuser")
    user.set_password("secret")
    db.session.add(user)
    db.session.commit()

    site = Site(
        title="Site Title",
        author="Site User",
        introduction="Welcome to my site.",
        navbar="#2196F3",
        footer="#2196F3",
        heroBackground="linear-gradient(135deg, #667eea, #764ba2)",
        user_id=user.id
    )
    db.session.add(site)
    db.session.commit()

    retrieved = Site.query.filter_by(user_id=user.id).first()
    assert retrieved is not None
    assert retrieved.title == "Site Title"

from app import db

class Article(db.Model):
    '''
    An Article contains the body of a blog post, as well as metadata for SEO tags.

    id              : int       : Primary key.
    author_name     : str(100)  : Author's full name. (Format: [First] [Last])
    author_twitter  : str(20)   : Author's Twitter handle.
    author_fbid     : str(20)   : Facebook page ID (optional).
    title           : str(75)   : Title of the article.
    slug            : str(100)  : Slug for navigation purposes.
    description     : str(160)  : Description of article; a hook, if you will.
    image           : str(255)  : Cover image URL. (Recommended: 1200px by 630px)
    section         : str(50)   : Section name. (Format: "POLITICS")
    tags            : str(255)  : Tags in a comma-separated list. (Format: "trump, biden, white house")
    body            : text      : The body of the article in HTML.
    created_at      : datetime  : When was the article created, in UTC time?
    modified_at     : datetime  : When was the article last modified, in UTC time?
    '''
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100))
    author_twitter = db.Column(db.String(20))
    author_fbid = db.Column(db.String(20))
    title = db.Column(db.String(75))
    slug = db.Column(db.String(100), unique=True, index=True)
    description = db.Column(db.String(160))
    image = db.Column(db.String(255))
    section = db.Column(db.String(50))
    tags = db.Column(db.String(255))
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Article {}>".format(self.slug)
    

class Feedback(db.Model):
    '''
    Feedback is a private reader response to an article.

    id          : int       : Primary key.
    article_id  : int       : Foreign key for Article object.
    email       : str(255)  : Poster's email address (optional).
    rating      : int       : Rating, 1-5.
    comments    : str(300)  : Additional comments (optional).
    created_at  : datetime  : When was this created, in UTC?
    '''
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    email = db.Column(db.String(255), index=True)
    rating = db.Column(db.Integer)
    comments = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Feedback {}>".format(self.created_at)
    

class Contact(db.Model):
    '''
    A Contact is someone who wants to be on the email list.

    id          : int       : Primary key.
    first_name  : str(50)   : Contact's first name (optional).
    last_name   : str(50)   : Contact's last name (optional).
    company     : str(100)  : Contact's company (optional).
    email       : str(255)  : Email address.
    opt_out     : bool      : Has the contact opted out of receiving emails? (If yes, don't email them anymore.)
    created_at  : datetime  : When was this created, in UTC?
    '''
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    company = db.Column(db.String(100))
    email = db.Column(db.String(255), index=True)
    opt_out = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Contact {}>".format(self.email)
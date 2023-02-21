from app.admin import bp
import json
from app.models import Article
from flask import request, abort, Response
from config import Config
import re
from app import db
import datetime
from slugify import slugify
import requests

@bp.route('/')
def hello():
    return "hello world"


@bp.route('/_admin/create/article', methods=['POST'])
def create_article():

    def length_check(string, max_length):
        assert len(string) <= int(max_length), "Length cannot exceed {} characters.".format(max_length)

    if str(request.form.get('publisher_key')) != Config.PUBLISHER_KEY:
        abort(403, description="Incorrect publisher_key.")
    
    # Convert to unsafe dictionary for convenience
    article_dict = {
        'author_name': request.form.get('author_name'),
        'author_twitter': request.form.get('author_twitter'),
        'author_fbid': request.form.get('author_fbid'),
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'image': request.form.get('image'),
        'section': request.form.get('section'),
        'tags': request.form.get('tags'),
        'body': request.form.get('body')
    }

    # Author name checks
    try:
        length_check(article_dict['author_name'], 100)
        assert re.search("^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}$", article_dict['author_name']) is not None, "Input is in the wrong format."
    except AssertionError as e:
        abort(400, description="`author_name` error: {}".format(e))

    # Author Twitter checks
    try:
        length_check(article_dict['author_twitter'], 20)
    except AssertionError as e:
        abort(400, description="`author_twitter` error: {}".format(e))

    # Author FBID checks
    if article_dict['author_fbid']:
        try:
            length_check(article_dict['author_fbid'], 20)
        except AssertionError as e:
            abort(400, description='`author_fbid` error: {}'.format(e))
    
    # Title checks
    try:
        length_check(article_dict['title'], 75)
    except AssertionError as e:
        abort(400, description="`title` error: {}".format(e))

    # Description checks
    try:
        length_check(article_dict['description'], 160)
    except AssertionError as e:
        abort(400, description="`description` error: {}".format(e))

    # Image checks
    try:
        length_check(article_dict['image'], 255)
        r = requests.get(article_dict['image'])
        assert r.status_code == 200, "Cannot load image."
    except AssertionError as e:
        abort(400, description="`image` error: {}".format(e))

    # Section checks
    try:
        length_check(article_dict['section'], 50)
    except AssertionError as e:
        abort(400, description='`section` error: {}'.format(e))

    # Tags check
    try:
        length_check(article_dict['tags'], 255)
        parse = article_dict['tags'].split(', ')
        assert len(parse) > 1, "Error parsing tags. Make sure they are in a comma-separated list. (Example: this, is, what, right, looks, like)"
    except AssertionError as e:
        abort(400, description="`tags` error: {}".format(e))

    # Body check
    try:
        assert len(article_dict['body']) > 0, "There is nothing in the article body."
    except AssertionError as e:
        abort(400, description="`body` error: {}".format(e))

    # Slug check
    try:
        slug = slugify(article_dict['title'])
        hits = Article.query.filter_by(slug=slug).first()
        assert not hits, "The title is not unique."
    except AssertionError as e:
        abort(400, description="`title` error: {}".format(e))

    # Commit to database
    try:
        article = Article()
        article.author_name = str(article_dict['author_name'])
        article.author_twitter = str(article_dict['author_twitter'])
        if not article_dict['author_fbid']:
            article.author_fbid = None
        else:
            article.author_fbid = str(article_dict['author_fbid'])
        article.title = str(article_dict['title'])
        article.description = str(article_dict['description'])
        article.image = str(article_dict['image'])
        article.section = str(article_dict['section']).upper()
        article.tags = str(article_dict['tags'])
        article.body = str(article_dict['body'])
        article.slug = slugify(article_dict['title'])
        article.created_at = datetime.datetime.utcnow()
        article.modified_at = datetime.datetime.utcnow()
        db.session.add(article)
        db.session.commit()

        return Response(
            status=201,
            response=json.dumps({
                'id': article.id,
                'author_name': article.author_name,
                'author_twitter': article.author_twitter,
                'author_fbid': article.author_fbid,
                'title': article.title,
                'slug': article.slug,
                'description': article.description,
                'image': article.image,
                'section': article.section,
                'tags': article.tags.split(', '),
                'body': "{}...".format(article.body[:99]),
                'created_at': datetime.datetime.strftime(article.created_at, '%Y-%m-%d %H:%M:%S'),
                'modified_at': datetime.datetime.strftime(article.modified_at, '%Y-%m-%d %H:%M:%S')
            }),
            mimetype='application/json'
        )
    except Exception as e:
        abort(500, description="Database error: {}".format(e))


@bp.route('/_admin/read/article/<slug>', methods=['GET'])
def read_article(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        abort(404, description="Article not found.")
    else:
        return Response(
            status=200,
            response=json.dumps({
                'id': article.id,
                'author_name': article.author_name,
                'author_twitter': article.author_twitter,
                'author_fbid': article.author_fbid,
                'title': article.title,
                'slug': article.slug,
                'description': article.description,
                'image': article.image,
                'section': article.section,
                'tags': article.tags.split(', '),
                'body': article.body,
                'created_at': datetime.datetime.strftime(article.created_at, '%Y-%m-%d %H:%M:%S'),
                'modified_at': datetime.datetime.strftime(article.modified_at, '%Y-%m-%d %H:%M:%S')
            }),
            mimetype='application/json'
        )


@bp.route('/_admin/update/article/<slug>', methods=['POST'])
def update_article(slug):
    if str(request.form.get('publisher_key')) != Config.PUBLISHER_KEY:
        abort(403, description="Incorrect publisher_key.")
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        abort(404, description="Article not found.")

    def length_check(string, max_length):
        assert len(string) <= int(max_length), "Length cannot exceed {} characters.".format(max_length)

    # Convert to unsafe dictionary for convenience
    article_dict = {
        'author_name': request.form.get('author_name'),
        'author_twitter': request.form.get('author_twitter'),
        'author_fbid': request.form.get('author_fbid'),
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'image': request.form.get('image'),
        'section': request.form.get('section'),
        'tags': request.form.get('tags'),
        'body': request.form.get('body')
    }

    # Author name checks
    try:
        length_check(article_dict['author_name'], 100)
        assert re.search("^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}$", article_dict['author_name']) is not None, "Input is in the wrong format."
    except AssertionError as e:
        abort(400, description="`author_name` error: {}".format(e))

    # Author Twitter checks
    try:
        length_check(article_dict['author_twitter'], 20)
    except AssertionError as e:
        abort(400, description="`author_twitter` error: {}".format(e))

    # Author FBID checks
    if article_dict['author_fbid']:
        try:
            length_check(article_dict['author_fbid'], 20)
        except AssertionError as e:
            abort(400, description='`author_fbid` error: {}'.format(e))

    # Description checks
    try:
        length_check(article_dict['description'], 160)
    except AssertionError as e:
        abort(400, description="`description` error: {}".format(e))

    # Image checks
    try:
        length_check(article_dict['image'], 255)
        r = requests.get(article_dict['image'])
        assert r.status_code == 200, "Cannot load image."
    except AssertionError as e:
        abort(400, description="`image` error: {}".format(e))

    # Section checks
    try:
        length_check(article_dict['section'], 50)
    except AssertionError as e:
        abort(400, description='`section` error: {}'.format(e))

    # Tags check
    try:
        length_check(article_dict['tags'], 255)
        parse = article_dict['tags'].split(', ')
        assert len(parse) > 1, "Error parsing tags. Make sure they are in a comma-separated list."
    except AssertionError as e:
        abort(400, description="`tags` error: {}".format(e))

    # Body check
    try:
        assert len(article_dict['body']) > 0, "There is nothing in the article body."
    except AssertionError as e:
        abort(400, description="`body` error: {}".format(e))

    # Title and slug checks
    try:
        length_check(article_dict['title'], 75)
        if article.title != article_dict['title']:
            slug = slugify(article_dict['title'])
            hits = Article.query.filter_by(slug=slug).first()
            assert not hits, "The title is not unique."
    except AssertionError as e:
        abort(400, description="`title` error: {}".format(e))
    
    try:
        article.author_name = str(article_dict['author_name'])
        article.author_twitter = str(article_dict['author_twitter'])
        if not article_dict['author_fbid']:
            article.author_fbid = None
        else:
            article.author_fbid = str(article_dict['author_fbid'])
        
        article.description = str(article_dict['description'])
        article.image = str(article_dict['image'])
        article.section = str(article_dict['section']).upper()
        article.tags = str(article_dict['tags'])
        article.body = str(article_dict['body'])
        if article.title != article_dict['title']:
            article.title = str(article_dict['title'])
            article.slug = slugify(article_dict['title'])
        article.modified_at = datetime.datetime.utcnow()
        db.session.commit()

        return Response(
            status=200,
            response=json.dumps({
                'id': article.id,
                'author_name': article.author_name,
                'author_twitter': article.author_twitter,
                'author_fbid': article.author_fbid,
                'title': article.title,
                'slug': article.slug,
                'description': article.description,
                'image': article.image,
                'section': article.section,
                'tags': article.tags.split(', '),
                'body': "{}...".format(article.body[:99]),
                'created_at': datetime.datetime.strftime(article.created_at, '%Y-%m-%d %H:%M:%S'),
                'modified_at': datetime.datetime.strftime(article.modified_at, '%Y-%m-%d %H:%M:%S')
            }),
            mimetype='application/json'
        )
    except Exception as e:
        abort(500, description="Database error: {}".format(e))


@bp.route('/_admin/delete/article/<slug>', methods=['POST'])
def delete_article(slug):
    if str(request.form.get('publisher_key')) != Config.PUBLISHER_KEY:
        abort(403, description="Incorrect publisher_key.")
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        abort(404, description="Article not found.")
    try:
        db.session.delete(article)
        db.session.commit()
        return Response(
            status=204,
            response='Article with slug {} successfully deleted.'.format(slug),
            mimetype='application/json'
        )
    except Exception as e:
        abort(500, description="Database error: {}".format(e))
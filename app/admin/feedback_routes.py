from app.admin import bp
from app.models import Article, Feedback
from config import Config
from flask import request, abort, Response
import json
import datetime

@bp.route('/_admin/read/feedbacks/<article_slug>', methods=['POST'])
def read_feedbacks(article_slug):
    if str(request.form.get('publisher_key')) != Config.PUBLISHER_KEY:
        abort(403, description="Incorrect publisher_key.")

    if article_slug != 'all':
        article = Article.query.filter_by(slug=article_slug).first()
        if not article:
            abort(404, description="Article with slug {} not found.".format(article_slug))
        feedbacks = Feedback.query.filter_by(article_id=article.id).order_by(Feedback.created_at.desc()).all()
    else:
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()

    data_list = []
    for feedback in feedbacks:
        data_dict = {
            'id': feedback.id,
            'article_id': feedback.article_id,
            'email': feedback.email,
            'rating': feedback.rating,
            'comments': feedback.comments,
            'created_at': datetime.datetime.strftime(feedback.created_at, '%Y-%m-%d %H:%M:%S')
        }
        data_list.append(data_dict)

    return Response(
        status=200,
        response=json.dumps(data_list),
        mimetype='application/json'
    )
from app.admin import bp
from app.models import Contact
from config import Config
from flask import request, abort, Response
import json
import datetime

@bp.route('/_admin/read/contacts', methods=['POST'])
def read_contacts():
    if str(request.form.get('publisher_key')) != Config.PUBLISHER_KEY:
        abort(403, description="Incorrect publisher_key.")
    data_list = []
    contacts = Contact.query.filter_by(opt_out=False).order_by(Contact.created_at.desc()).all()
    for contact in contacts:
        data_dict = {
            'id': contact.id,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'company': contact.company,
            'email': contact.email,
            'created_at': datetime.datetime.strftime(contact.created_at, '%Y-%m-%d %H:%M:%S')
        }
        data_list.append(data_dict)
    return Response(
        status=200,
        response=json.dumps(data_list),
        mimetype='application/json'
    )

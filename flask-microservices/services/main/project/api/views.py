# /services/main/project/api/views.py


from flask import Blueprint, jsonify, request, make_response

from project.api.models import Name
from project import db


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'success',
        'message': 'Hello, World!'
    })


@main_blueprint.route('/names', methods=['POST'])
def add_name():
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    name = post_data.get('name')
    if not name:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    new_name = Name.query.filter_by(name=name).first()
    if not new_name:
        db.session.add(Name(name=name))
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'{name} was added!'
        }
        return make_response(jsonify(response_object)), 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'Name already exists.'
        }
        return make_response(jsonify(response_object)), 400


@main_blueprint.route('/names/<name_id>', methods=['GET'])
def get_single_name(name_id):
    """
    Get single name details
    """
    try:
        name = Name.query.filter_by(id=name_id).first()
        response_object = {
            'status': 'success',
            'data': {'name': name.name}
        }
        return make_response(jsonify(response_object)), 200
    except:
        response_object = {
            'status': 'fail',
            'message': 'Name does not exist.'
        }
        return make_response(jsonify(response_object)), 404

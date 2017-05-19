# /services/names/project/api/views.py


from flask import Blueprint, jsonify, request, make_response, \
    render_template

from project.api.models import Name
from project import db


names_blueprint = Blueprint(
    'names', __name__, template_folder='./templates')


@names_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        name = Name(text)
        db.session.add(name)
        db.session.commit()
    names = Name.query.order_by(Name.created_date.desc()).all()
    return render_template('index.html', names=names)


@names_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@names_blueprint.route('/names', methods=['GET'])
def get_all_names():
    """Get all names"""
    names = Name.query.all()
    names_list = []
    for name in names:
        name_object = {
            'id': name.id,
            'text': name.text,
            'created_date': name.created_date
        }
        names_list.append(name_object)
    response_object = {
        'status': 'success',
        'data': {
          'names': names_list
        }
    }
    return make_response(jsonify(response_object)), 200


@names_blueprint.route('/names/<name_id>', methods=['GET'])
def get_single_name(name_id):
    """Get single name details"""
    response_object = {
        'status': 'fail',
        'message': 'Name does not exist'
    }
    try:
        name = Name.query.filter_by(id=int(name_id)).first()
        if not name:
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                  'name': name.text,
                  'created_date': name.created_date
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404


@names_blueprint.route('/names', methods=['POST'])
def add_name():
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    text = post_data.get('text')
    if not text:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    new_text = Name.query.filter_by(text=text).first()
    if not new_text:
        db.session.add(Name(text=text))
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'{text} was added!'
        }
        return make_response(jsonify(response_object)), 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'Name already exists.'
        }
        return make_response(jsonify(response_object)), 400

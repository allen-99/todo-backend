from flask import Blueprint, jsonify, request, session
from db import mongo
import json
from bson.objectid import ObjectId

main = Blueprint('main', __name__)
db = mongo.db


@main.route('/hello', methods=['POST'])
def hello():
    data = request.get_json()
    name = data['first']
    password = data['second']

    return jsonify({'message': [name, password, 'help']})


@main.route('/todos', methods=['POST'])
def add_todo():
    request_data = request.get_json()
    # if "login" not in session:
    #     return jsonify({'message': 'user not authorization'})
    # email = session["login"]
    print(request_data)
    tag_id = request_data['tag_id']
    place = request_data['place']
    date_begin = request_data['date_begin']
    date_end = request_data['date_end']

    tags_find = db.tags.find({'tag_id': {'$ne': 0}})
    tags = [tag for tag in tags_find]  # list of dict

    if tag_id == '':
        tag_id = 0
    if place == '':
        place = None

    tag_name = 'Не выбрано'
    for tag in tags:
        if int(tag.get('tag_id')) == int(tag_id):
            tag_name = tag.get('tag_name')

    todo = db.event.insert_one({
        'date_begin': date_begin,
        'date_end': date_end,
        'group_id': int(request_data['group_id']),
        'header': request_data['header'],
        'place': place,
        'tag_id': tag_id,
        'text': request_data['text'],
        'is_done': False
    })

    return json.dumps({'todo_id': todo.inserted_id, 'tag_name': tag_name} , default=str)


@main.route('/todos', methods=['GET'], strict_slashes=False)
def get_todos():
    todos = db.event.find()
    a = [todo for todo in todos]

    return json.dumps(a, default=str)


@main.route('/columns', methods=['GET'], strict_slashes=False)
def get_columns():
    columns = db.group.find()
    a = [todo for todo in columns]

    return json.dumps(a, default=str)


@main.route('/todos/<int:column_id>', methods=['GET'], strict_slashes=False)
def get_todos_from_one_column(column_id):
    todos = db.event.find({'group_id': column_id, 'is_done': False})
    tags_find = db.tags.find({'tag_id': {'$ne': 0}})
    tags = [tag for tag in tags_find]  #list of dict
    a = [todo for todo in todos]

    for todo in a:
        todo_tag_id = todo.get('tag_id')
        tag_name = 'Не выбрано'
        for tag in tags:
            if int(tag.get('tag_id')) == int(todo_tag_id):
                tag_name = tag.get('tag_name')
        todo.update({'tag_name': tag_name})

    return json.dumps(a, default=str)


@main.route('/delete_todo', methods=['POST'], strict_slashes=False)
def delete_todo():
    request_data = request.get_json()
    todo_id = request_data['_id']
    todo = db.event.delete_one({'_id': ObjectId(todo_id)})
    return todo.raw_result


@main.route('/edit_todo', methods=['POST'], strict_slashes=False)
def edit_post():
    request_data = request.get_json()
    todo_id = request_data['_id']
    tag_id = request_data['tag_id']
    place = request_data['place']
    date_begin = request_data['date_begin']
    date_end = request_data['date_end']

    tags_find = db.tags.find({'tag_id': {'$ne': 0}})
    tags = [tag for tag in tags_find]  # list of dict

    if tag_id == '':
        tag_id = 0
    if place == '':
        place = None

    tag_name = 'Не выбрано'
    for tag in tags:
        if int(tag.get('tag_id')) == int(tag_id):
            tag_name = tag.get('tag_name')

    todo = db.event.update_one({'_id': ObjectId(todo_id)}, {'$set': {
        'date_begin': date_begin,
        'date_end': date_end,
        'group_id': int(request_data['group_id']),
        'header': request_data['header'],
        'place': place,
        'tag_id': tag_id,
        'text': request_data['text']
    }})

    return json.dumps({'tag_name': tag_name}, default=str)


@main.route('/add_column', methods=['POST'], strict_slashes=False)
def add_column():
    request_data = request.get_json()
    group_name = request_data['group_name']
    desk_id = request_data['desk_id']

    columns = db.group.find()
    a = [column for column in columns]
    if a != []:
        group_id = a[-1]['group_id'] + 1
    else:
        group_id = 0

    column = db.group.insert_one({
        'group_id': group_id,
        'group_name': group_name,
        'desk_id': desk_id
    })

    return json.dumps([column.inserted_id, group_id], default=str)


@main.route('/edit_column', methods=['POST'], strict_slashes=False)
def edit_column_name():
    request_data = request.get_json()
    group_name = request_data['group_name']
    group__id = request_data['_id']
    group_id = request_data['group_id']
    desk_id = request_data['desk_id']

    column = db.group.update_one({'_id': ObjectId(group__id)}, {'$set': {
        'group_name': group_name,
        'group_id': group_id,
        'desk_id': desk_id
    }})

    return column.raw_result


@main.route('/delete_column', methods=['POST'], strict_slashes=False)
def delete_column():
    request_data = request.get_json()
    column_id = request_data['_id']
    column = db.group.delete_one({'_id': ObjectId(column_id)})
    db.event.delete_many({'group_id': request_data['group_id']})
    return column.raw_result


@main.route('/done_todo', methods=['POST'], strict_slashes=False)
def done_todo():
    request_data = request.get_json()
    print(request_data)
    todo_id = request_data['_id']
    todo = db.event.update_one({'_id': ObjectId(todo_id)}, {'$set': {
        'is_done': True
    }})

    return todo.raw_result


@main.route('/done_todo', methods=['GET'], strict_slashes=False)
def get_done_todo():
    todos = db.event.find({'is_done': True})
    a = [todo for todo in todos]

    return json.dumps(a, default=str)


@main.route('/tags',  methods=['GET'], strict_slashes=False)
def get_tags():
    tags = db.tags.find({'tag_id': {'$ne': 0}})
    a = [tag for tag in tags]
    
    return json.dumps(a, default=str)


@main.route('/delete_tag', methods=['POST'], strict_slashes=False)
def delete_tag():
    request_data = request.get_json()
    column_id = request_data['_id']
    column = db.tags.delete_one({'_id': ObjectId(column_id)})
    db.event.update_many({'tag_id': column_id}, {"$set": {'tag_id': 0}})
    return column.raw_result


@main.route('/add_tag', methods=['POST'], strict_slashes=False)
def add_tag():
    request_data = request.get_json()
    print(request_data)

    tags = db.tags.find()
    a = [tag for tag in tags]
    if a != []:
        tag_id = a[-1]['tag_id'] + 1
    else:
        tag_id = 1

    tag = db.tags.insert_one({
        'tag_id': tag_id,
        'tag_name': request_data['tag_name']
    })

    return json.dumps([tag.inserted_id, tag_id], default=str)
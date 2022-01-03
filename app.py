import threading

from flask import Flask, jsonify, abort, request

app = Flask(__name__)
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# tasks = [
#     {
#         'id': 1,
#         'title': u'Buy groceries',
#         'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
#         'done': False
#     },
#     {
#         'id': 2,
#         'title': u'Learn Python',
#         'description': u'Need to find a good Python tutorial on the web',
#         'done': False
#     }
# ]
#
# def give_data():
#     data = {
#         "user_id": int,
#         "data": {
#             "x_data_type": str,
#             "y_data_type": str,
#             "x": [
#                 {
#                     "date": '2012-11-05',
#                     "value": 12.4,
#                 },
#                 {
#                     "date": '2022-11-03',
#                     "value": 10.4,
#                 }, {
#                     "date": '2022-11-01',
#                     "value": 8.4,
#                 }
#             ],
#             "y": [
#                 {
#                     "date": '2022-11-01',
#                     "value": 7.2,
#                 },
#                 {
#                     "date": '2022-11-03',
#                     "value": 11.5,
#                 }, {
#                     "date": '2022-11-03',
#                     "value": 15.7,
#                 }
#             ]
#         }
#     }
#     return data
#
#
# data_my = give_data()
#
def processing(data_my):
    data_x = data_my['data']['x']
    data_y = data_my['data']['y']
    data_x = [{'date': datetime.timestamp(datetime.strptime(x['date'], "%Y-%m-%d")), 'value': x['value']} for x in data_x]

    data_x.sort(key=lambda x: x['date'])

    data_y = [{'date': datetime.timestamp(datetime.strptime(y['date'], "%Y-%m-%d")), 'value': y['value']} for y in data_y]

    data_y.sort(key=lambda y: y['date'])
    print(data_x)
    print(data_y)

    data_col = {}
    for el in data_x:
        if not el['date'] in data_col:
            help_y = list(filter(lambda y: y['date'] == el['date'], data_y))
            help_x = list(filter(lambda x: x['date'] == el['date'], data_x))
            if len(help_y) >= 1 and len(help_x) >= 1:
                data_col[help_x[0]['date']] = {'x': help_x[0]['value'], 'y': help_y[0]['value']}
            else:
                print(0)
    print(data_col)
    df = pd.DataFrame(
        {
            'x': [data_col[key]['x'] for key in data_col.keys()],
            'y': [data_col[key]['y'] for key in data_col.keys()]
        }
    )
    print(df['x'].corr(df['y']))
    pd.DataFrame(np.array([df['x'], df['y']]).T).plot.scatter(0, 1, s=12, grid=True)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()
#
@app.route('/test', methods=['POST'])
def get_tasks():# Получил данные
    data = request.json
    print(data)
    my_thread = threading.Thread(target=processing, args=(data,))
    my_thread.start()
    return '200'
    # return jsonify({'tasks': tasks})
#
#
# @app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
# def get_task(task_id):
#     task = filter(lambda t: t['id'] == task_id, tasks)
#     if len(task) == 0:
#         abort(404)
#     return jsonify({'task': task[0]})
#
#
# @app.route('/')
# def index():
#     return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)


# import matplotlib.pyplot as plt
# df = pd.DataFrame({
#     'length': [1.5, 0.5, 1.2, 0.9, 3],
#     'width': [0.7, 0.2, 0.15, 0.2, 1.1]
# }, index=['pig', 'rabbit', 'duck', 'chicken', 'horse'])
#
# x = df['lenght'].apply(jitter(0.5))
# hist = df.hist(bins=5)
# plt.show()


# df = pd.DataFrame({
#     'x': [1, 2, 2],
#     'y': [5, 6, 7]
# })
#
# help = df['x'].mean()
# print(help)
# print(sum(df['x'] - help))
# n = 30
#
# n = n - 1 if n in range(1, 30) else n
#
# print(n)

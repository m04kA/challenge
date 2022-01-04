from flask import Flask, jsonify, abort, request
from datetime import datetime
import threading
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymongo
from mongoLib import *

app = Flask(__name__)


#
# def give_data():
#     data = {
#         "user_id": 1,
#         "data": {
#             "x_data_type": "t",
#             "y_data_type": "h",
#             "x": [
#                 {
#                     "date": "2012-11-05",
#                     "value": 12.4
#                 },
#                 {
#                     "date": "2022-11-03",
#                     "value": 10.4
#                 }, {
#                     "date": "2022-11-01",
#                     "value": 8.4
#                 },{
#                     "date": "2020-11-03",
#                     "value": 79.1
#                 },{
#                     "date": "2019-11-03",
#                     "value": 19.4
#                 }
#                 ,{
#                     "date": "2018-11-03",
#                     "value": 15.4
#                 }
#             ],
#             "y": [
#                 {
#                     "date": "2022-11-01",
#                     "value": 7.2
#                 },
#                 {
#                     "date": "2022-11-03",
#                     "value": 11.5
#                 }, {
#                     "date": "2022-11-03",
#                     "value": 15.7
#                 },
#                 {
#                     "date": "2020-11-03",
#                     "value": 57.4
#                 },
#                 {
#                     "date": "2019-11-03",
#                     "value": 20.4
#                 },{
#                     "date": "2018-11-03",
#                     "value": 15.4
#                 }
#             ]
#         }
#     }
#     return data
#
#
# data_my = give_data()
#

def conecting_to_DB(name_DB, name_collection, port=27017):
    client = pymongo.MongoClient(port=port)
    DB = client[name_DB]
    collection_name = DB[name_collection]
    return collection_name


def processing(data_my):
    """
    Processing data for uploading to the database
    :param data_my:
    :return:
    """
    # ----Sorting by time field----
    data_x = data_my['data']['x']
    data_y = data_my['data']['y']
    data_x = [{'date': datetime.timestamp(datetime.strptime(x['date'], "%Y-%m-%d")), 'value': x['value']} for x in
              data_x]
    data_y = [{'date': datetime.timestamp(datetime.strptime(y['date'], "%Y-%m-%d")), 'value': y['value']} for y in
              data_y]

    data_x.sort(key=lambda x: x['date'])
    data_y.sort(key=lambda y: y['date'])
    # ----------------------------
    # print(data_x)
    # print(data_y)

    # ----Data dictionary----
    data_information = {}
    data_information['user_id'] = data_my['user_id']
    data_information["x_data_type"] = data_my['data']["x_data_type"]
    data_information["y_data_type"] = data_my['data']["y_data_type"]
    data_information['data'] = {}
    data_col = data_information['data']
    for el in data_x:
        if not el['date'] in data_col:
            help_y = list(filter(lambda y: y['date'] == el['date'], data_y))
            help_x = list(filter(lambda x: x['date'] == el['date'], data_x))
            if len(help_y) >= 1 and len(help_x) >= 1:
                data_col[str(help_x[0]['date'])] = {'x': help_x[0]['value'], 'y': help_y[0]['value']}
            else:
                print(0)
    # -----------------------
    # ----Plot points----
    # print(data_information)
    # df = pd.DataFrame(
    #     {
    #         'x': [data_col[key]['x'] for key in data_col.keys()],
    #         'y': [data_col[key]['y'] for key in data_col.keys()]
    #     }
    # )
    # print(df['x'].corr(df['y']))
    # pd.DataFrame(np.array([df['x'], df['y']]).T).plot.scatter(0, 1, s=12, grid=True)
    # plt.xlabel('X')
    # plt.ylabel('Y')
    # plt.show()
    # ------------------
    # ----Connect with database----
    collection_name = conecting_to_DB("challenge", "Correlation_data")
    # -------------------------------
    result = find_document(collection_name, {'user_id': data_information['user_id']})

    if result:
        data_information['data'] = result['data'] | data_information['data']
        update_document(collection_name, {'_id': result['_id']}, {'data': data_information['data']})
    else:
        insert_document(collection_name, data_information)
    # print(result)


#
@app.route('/calculate', methods=['POST'])
def get_tasks():  # Получил данные
    data = request.json
    print(data)
    my_thread = threading.Thread(target=processing, args=(data,))
    my_thread.start()
    return '200'
    # return jsonify({'tasks': tasks})


# x_data_type=<string:x_data_type>&y_data_type=<string:y_data_type>&user_id=<int:user_id>
@app.route('/correlation', methods=['GET'])
def get_task():
    x_data_type = request.args.get('x_data_type', default='', type=str)
    y_data_type = request.args.get('y_data_type', default='', type=str)
    user_id = request.args.get('user_id', default=-1, type=int)
    collection_name = conecting_to_DB("challenge", "Correlation_data")
    data = find_document(collection_name, {'user_id': user_id, 'x_data_type': x_data_type, 'y_data_type': y_data_type})
    if len(data) == 0:
        abort(404)
        return 'Error'
    del data['_id']
    print(type(data))
    print(data)
    return jsonify({"answ": data})


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

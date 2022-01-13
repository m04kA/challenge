import pandas
from flask import Flask, jsonify, abort, request
from datetime import datetime
import threading
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mongoLib import *
from scipy import stats

app = Flask(__name__)


def conecting_to_DB(name_DB, name_collection, port=27017):
    client = pymongo.MongoClient(port=port)
    DB = client[name_DB]
    collection_name = DB[name_collection]
    return collection_name


def plot_with_points(data):
    values_x = []
    values_y = []
    for key in data['data'].keys():
        values_x.append(data['data'][key]['x'])
        values_y.append(data['data'][key]['y'])
    df = pd.DataFrame(
        {
            'x': values_x,
            'y': values_y
        }
    )
    pd.DataFrame(np.array([df['x'], df['y']]).T).plot.scatter(0, 1, s=12, grid=True)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()


def to_type_date(date):
    """
    This funk for delete row with bad date.
    :param date:
    :return: clear & good data with correct date
    """
    try:
        date['date'] = pd.to_datetime(date['date'], yearfirst=True, format='%Y-%m-%d')
    except ValueError as ex:
        ex = str(ex)
        wrong_key = ex[ex.find("data") + len("data") + 1: ex.find("doesn") - 1]
        date.drop(date.loc[date['date'] == wrong_key].index, inplace=True)
        print(f'Wrong date - {wrong_key}')
        to_type_date(date)
    return date


def processing(data_my: dict):
    """
    Processing data for uploading to the database
    :param data_my:
    :return:
    """
    global flag

    # ---- Checking user_id ----
    data_information = {}
    if type(data_my['user_id']) == int:
        data_information['user_id'] = data_my['user_id']
    else:
        flag = "User`s id is not int."
        raise TypeError('User`s id is not int.')
    # ---------------------

    # ---- Checking the availability of data ----
    if not 'data' in data_my:
        flag = "There is no data."
        raise ValueError("There is no data.")
    # -----------------------------

    data_information['data'] = {}
    data_col = data_information['data']

    # ---- Checking data types ----
    mass_names_dict_values = []
    for key in data_my['data'].keys():
        if type(data_my['data'][key]) == str:
            name_dict_values = key.split('_')[0]
            if (name_dict_values in data_my['data']) and not (name_dict_values in mass_names_dict_values):
                if len(data_my['data'][name_dict_values]) != 0:
                    mass_names_dict_values.append(name_dict_values)
                    data_col[key] = data_my['data'][key]
    # ---------------------

    # ----Sorting by time field----
    for key in mass_names_dict_values:
        data_x = pd.DataFrame(
            {"date": [data_my['data'][key][ind]['date'] for ind in range(len(data_my['data'][key]))],
             "values": [data_my['data'][key][ind]['value'] for ind in range(len(data_my['data'][key]))]})
        data_x = to_type_date(data_x)
        data_x = data_x.sort_values(by="date")

    # data_y = pd.DataFrame(
    #     {"date": [data_my['data']['y'][ind]['date'] for ind in range(len(data_my['data']['y']))],
    #      "values": [data_my['data']['y'][ind]['value'] for ind in range(len(data_my['data']['y']))]})
    # try:
    #     data_y['date'] = pd.to_datetime(data_y['date'], yearfirst=True, format='%Y-%m-%d')
    # except Exception as exept:
    #     print(f'Wrong date - {exept}')

    # data_y = data_y.sort_values(by="date")
    # ----------------------------

    # ----Data dictionary----

    for ind in range(data_x.count()[0]):
        if not data_x.loc[ind, 'date'] in data_col:
            help_y = data_y[
                data_y['date'] == data_x.loc[ind, 'date']]  # list(filter(lambda y: y['date'] == el['date'], data_y))
            help_x = data_x[
                data_x['date'] == data_x.loc[ind, 'date']]  # list(filter(lambda x: x['date'] == el['date'], data_x))

            if len(help_y) >= 1 and len(help_x) >= 1:
                # print(f'{help_y.index}  --  {help_y.index[-1]}')
                # print(f'{help_x.index}  --  {help_x.index[-1]}')
                data_col[str(help_x['date'].values[-1])[:10]] = \
                    {
                        'x': help_x['values'].values[-1],
                        'y': help_y['values'].values[-1]
                    }
            else:
                # print(0)
                continue
    # -----------------------
    # plot_with_points(data_information) # Plot with points
    # ----Connect with database----
    collection_name = conecting_to_DB("challenge", "Correlation_data")

    result = find_document(collection_name,
                           {'user_id': data_information['user_id'], 'x_data_type': data_information['x_data_type'],
                            'y_data_type': data_information['y_data_type']})

    if result:
        data_information['data'] = result['data'] | data_information['data']
        update_document(collection_name, {'_id': result['_id']}, {'data': data_information['data']})
    else:
        insert_document(collection_name, data_information)
    # print(result)
    flag = "All good"
    # exit(0)
    # -------------------------------


# http://127.0.0.1:5000//calculate
@app.route('/calculate', methods=['POST'])
def get_tasks():  # Получил данные
    data = request.json
    print("POST working")
    global flag
    flag = ""
    my_thread = threading.Thread(target=processing, args=(data,))
    my_thread.start()
    my_thread.join()
    return flag


# http://127.0.0.1:5000/correlation?x_data_type=steps_on_x&y_data_type=steps_on_y&user_id=1
@app.route('/correlation', methods=['GET'])
def get_task():
    x_data_type = request.args.get('x_data_type', default='', type=str)
    y_data_type = request.args.get('y_data_type', default='', type=str)
    user_id = request.args.get('user_id', default=-1, type=int)
    collection_name = conecting_to_DB("challenge", "Correlation_data")
    data = find_document(collection_name, {'user_id': user_id, 'x_data_type': x_data_type, 'y_data_type': y_data_type})
    if not data:
        abort(404)
    del data['_id']
    values_x = []
    values_y = []
    for key in data['data'].keys():
        values_x.append(data['data'][key]['x'])
        values_y.append(data['data'][key]['y'])
    df = pd.DataFrame(
        {
            'x': values_x,
            'y': values_y
        }
    )
    pearson_value, pearson_p_value = stats.pearsonr(df['x'], df['y'])
    answer = {
        "user_id": data['user_id'],
        "x_data_type": data["x_data_type"],
        "y_data_type": data["y_data_type"],
        "correlation": {
            "value": pearson_value,
            "p_value": pearson_p_value,
        }
    }
    return jsonify(answer)


#
#
# @app.route('/')
# def index():
#     return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)

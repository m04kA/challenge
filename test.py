import pandas as pd

a = {
    "user_id": 1,
    "data": {
        "x_data_type": "steps_on_x",
        "y_data_type": "steps_on_y",
        "z_data_type": "steps_on_y",
        "x": [
            {
                "date": "2012-11-05",
                "value": 12.4
            },
            {
                "date": "2022-11-03",
                "value": 10.4
            },
            {
                "date": "2022-11-01",
                "value": 8.4
            },
            {
                "date": "2020-11-03",
                "value": 79.1
            },
            {
                "date": "ggg",
                "value": 19.4
            },
            {
                "date": "2018/11/03",
                "value": 15.4
            }
        ]
    }
}

data_x = pd.DataFrame(
    {
        'date': [a['data']['x'][ind]['date'] for ind in range(len(a['data']['x']))],
        'values': [a['data']['x'][ind]['value'] for ind in range(len(a['data']['x']))]
    }
)


def to_type_date(date):
    try:
        date['date'] = pd.to_datetime(date['date'], yearfirst=True, format='%Y-%m-%d')
    except ValueError as ex:
        ex = str(ex)
        wrong_key = ex[ex.find("data") + len("data") + 1: ex.find("doesn") - 1]
        date.drop(date.loc[date['date'] == wrong_key].index, inplace=True)
        print(f'Wrong date - {wrong_key}')
        to_type_date(date)
    return date


data_x = to_type_date(data_x)

# except Exception as ex:
#     print(ex)
# data_x = data_x.sort_values(by="date")
# print(test)
print('------------')
print(data_x)

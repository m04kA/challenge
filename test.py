a = {}
a['user_id'] = 2
a["x_data_type"] = 'hh'
a["y_data_type"] = 'gg'
a['data'] = {}

b = a['data']

b['x'] = [
    {
        "date": "2012-11-05",
        "value": 12.4
    },
    {
        "date": "2022-11-03",
        "value": 10.4
    }
]

rc = '2'
if type(rc) == int:
    print(1)
else:
    raise TypeError('Bad type!')

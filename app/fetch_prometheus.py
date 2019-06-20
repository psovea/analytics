import requests
from datetime import datetime
import numpy
import urllib.parse

# URL for the Prometheus database.
# prom_database_addr = 'http://18.224.29.151:9090/api/v1/query?query='
prom_database_addr = 'http://localhost:9090/api/v1/query?query='

def make_prom_query(query):
    """Make a query to the Prometheus database and returns the result."""
    request_result = requests.get(prom_database_addr + urllib.parse.quote(query))
    return request_result.json()


def check_json_result(json_result):
    """Check whether the query was succesful or not."""
    return json_result['status'] == 'success'


def get_data_json_result(json_result):
    """Extract the data from a json object."""
    return json_result['data']['result']


def get_type_json_result(json_result):
    """Extract the data type from json object."""
    return json_result['data']['resultType']


def create_labels(label_list):
    """label list should be a list of tuples with the first the label name
    and the second the label value, e.g. [(operator, GVB), (district, CENTRUM)],
    the result you get when taking {}.items()"""
    return ", ".join([str(name) + '=~"' + str(value) + '"' for name, value in label_list if value])


def create_prom_query(query_json):
    """ Creates a prometheus query from a json object

    example json:
{'sum':
    {'or': [
        {'increase':
            {
                'metric': 'location_punctuality',
                'labels': {'district': 'West'},
                'period': '1d',
                'offset': '1d'
            }
        }, 
        {'increase':
            {
                'metric': 'location_punctuality',
                'labels': {'district': 'Centrum'},
                'period': '1d',
                'offset': '1d'
            }
        }]
    },
'by': ['transport_type']
}
    """
    res_str = ''
    for component_type, inner in query_json.items():
        if component_type == 'or':
            res_str += ' or '.join([create_prom_query(subquery) for subquery in inner])
        elif component_type == 'and':
            res_str += ' and '.join([create_prom_query(subquery) for subquery in inner])
        elif component_type == 'metric':
            res_str += str(inner)
        elif component_type == 'labels':
            res_str += "{" + str(create_labels(inner.items())) + "}"
        elif component_type == 'period':
            res_str += "[" + str(inner) + "]"
        elif component_type == 'offset':
            res_str += ' offset ' + str(inner)
        elif component_type == 'by':
            res_str += ' by (' + ','.join(inner) + ')'
        elif component_type == 'topk':
            print(inner)
            res_str += ' topk(' + inner['k'] + ',' + create_prom_query(inner['subquery']) + ')'
        elif component_type == '+':
            res_str += " + ".join([create_prom_query(subquery) for subquery in inner])
        else:
            res_str += str(component_type) + '(' + str(create_prom_query(inner)) + ')'
    return res_str


def execute_json_prom_query(json_query):
    """Executes the query from the json_query and returns the result"""
    query_string = create_prom_query(json_query)
    print(query_string)
    query_res = make_prom_query(query_string)
    print(query_res)
    if check_json_result(query_res):
        return get_data_json_result(query_res)
    else:
        print('Prometheus query failed:', query_string)


def create_template_labels(start_template, districts=[], transport_types=[],
                           operators=[], line_numbers=[]):
    """Create template for Prometheus query with different filters."""
    a = [districts, transport_types, operators]
    combinations = [list(x) for x in
                    numpy.array(numpy.meshgrid(*a)).T.reshape(-1, len(a))]
    subqueries = []
    for district, transport_type, operator in combinations:
        labels = create_labels(
            [("district", district), ("transport_type", transport_type), ("operator", operator)])
        subqueries.append(start_template % (labels, '%d', '%d'))
    return ' or '.join(subqueries), len(combinations)


def remove_unwanted_keys(dictionary, keys):
    """Remove unwanted filters from the dictionary with filters."""
    for key in keys:
        del dictionary[key]
    return dictionary


def top_ten_bottlenecks(start_day_time, end_day_time, days, period,
                        districts=[], transport_types=[], operators=[],
                        return_filters=[], line_numbers=[]):
    """Determine the top ten places that have the most/longest delays.

    start_day_time, end_day_time: period on the day which should be considered
    (_day_time should be given by seconds since 0:00).
    days: list of days which should be considered with 0 monday, 1 tuesday etc.
    period: the total time which should be considered, in days.
    NOTE: does not consider the current day if end_day_time is after current
    time.
    """
    query_template = 'increase(location_punctuality{%s}[%ss] offset %ss)'
    if return_filters:
        query_template = "sum(" + ") by ("
    query_template, amount = create_template_labels(query_template, districts,
                                                    transport_types, operators,
                                                    line_numbers)
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0,
                                                microsecond=0)).total_seconds()
    offset = seconds_since_midnight - end_day_time
    time_range = end_day_time - start_day_time
    today = datetime.today().weekday()

    results = {}
    for day in range(period + 1):
        if offset > 0 and (today - day) % 7 in days:
            query = query_template % ((time_range, offset) * amount)
            result = make_prom_query(query)
            if check_json_result(result):
                data = get_data_json_result(result)
                if data:
                    for metric in data:
                        key = tuple(remove_unwanted_keys(metric['metric'],
                                                         return_filters).items())
                        value = float(metric['value'][1])
                        if key in results:
                            results[key] += value
                        else:
                            results[key] = value
            else:
                print('Query to Prometheus database went wrong, status error' +
                      'code: %s' % (result['status']))
        offset += 86400  # seconds in a day
    results = [{'metric': dict(filt), 'value': val} for filt, val in
               results.items()]
    results.sort(key=lambda x: x['value'], reverse=True)
    print(results)
    return results


def heatmap_punctuality(period='d', vehicle_type=None, operator=None,
                        area=None):
    """Calculate punctuality between 2 locations to show it on the heatmap."""
    # Select the correct labels based on given filters.
    labels = ''
    if vehicle_type:
        labels += 'transport_type="%s"' % vehicle_type

    if operator and vehicle_type:
        labels += ', operator="%s"' % operator
    elif operator:
        labels += 'operator="%s"' % operator

    if (area and vehicle_type) or (area and operator):
        labels += ', district="%s"' % area
    elif area:
        labels += 'district="%s"' % area

    # Make and do the query.
    query = 'increase(location_punctuality{%s}[1%s])' % (labels,
                                                         period)
    result = make_prom_query(query)

    # Make a dictionary with weights as values and stopcodes as keys.
    dct = {}
    if check_json_result(result):
        data = get_data_json_result(result)
        for l in data:
            begin, end = l['metric']['stop_begin'], l['metric']['stop_end']
            value = float(l['value'][1])
            if begin not in dct.keys():
                dct[begin] = {}
            dct[begin][end] = value
    else:
        print('Query to Prometheus database went wrong, status error code: %s'
              % (result['status']))

    return dct


def donut_districts(amount=1, unit='d'):
    """Make a JSON object with mean delay per city district."""
    query = 'sum(increase(location_punctuality[%d%s])) by (district)' % (
        amount, unit)
    result = make_prom_query(query)

    dct = {}
    if check_json_result(result):
        data = get_data_json_result(result)
        for l in data:
            dct[l['metric']['district']] = float(l['value'][1])
    else:
        print('Query to Prometheus database went wrong, status error code: %s'
              % (result['status']))

    return [{key: val} for (key, val) in
            sorted(dct.items(), key=lambda kv: kv[1], reverse=True)]

if __name__ == '__main__':
    print(execute_json_prom_query(
{'sort_desc':
    {'sum':
    {'or': [
        {'increase':
            {
                'metric': 'location_punctuality',
                'labels': {'district': 'West'},
                'period': '1d',
                'offset': '1d'
            }
        }, 
        {'increase':
            {
                'metric': 'location_punctuality',
                'labels': {'district': 'Centrum'},
                'period': '1d',
                'offset': '1d'
            }
        }]
    },
    'by': ['transport_type']
}
}))
    
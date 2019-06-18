import requests
from datetime import datetime
import numpy

prom_database_addr = 'http://18.224.29.151:9090/api/v1/query?query='
time_period = 5  # in minutes

def make_prom_query(query):
    """Make a query to the Prometheus database and returns the result."""
    result = {}
    try:
        request_result = requests.get(prom_database_addr + query)
        result = request_result.json()
    except requests.exceptions.ConnectionError as e:
        print("error message:", e)
        result['status'] = "error"

    return result

def check_json_result(json_result):
    """Check whether the query was succesful or not."""
    return json_result['status'] == 'success'


def get_data_json_result(json_result):
    """Extract the data from a json object."""
    return json_result['data']['result']  # Metric dict and value list


def get_type_json_result(json_result):
    """Extract the data type from json object."""
    return json_result['data']['resultType']

def create_template_labels(start_template, districts=[], transport_types=[], operators=[]):
    """"""
    a = [districts, transport_types, operators]
    combinations = [list(x) for x in numpy.array(numpy.meshgrid(*a)).T.reshape(-1,len(a))]
    subqueries = []
    for district, transport_type, operator in combinations:
        labels = 'district="' + str(district) + '", transport_type="' + str(transport_type) + '", operator="' + str(operator) + '"'
        subqueries.append(start_template % (labels, '%d', '%d'))
    return ' or '.join(subqueries), len(combinations)

def remove_unwanted_keys(dictionary, keys):
    for key in keys:
        del dictionary[key]
    return dictionary

# over how much time??? --> for all statistics
def top_ten_bottlenecks(start_day_time, end_day_time, days, period, districts=[],
                        transport_types=[], operators=[], return_filters=[]):
    """Determine the top ten places that have the most/longest delays.
    start_day_time and end_day_time give the period on the day which should be considered
    (_day_time should be given by seconds since 0:00).
    days is the list of days which should be considered, with 0 monday, 1 tuesday etc.
    period is the the total time which should be considered, in days.
    NOTE: does not consider the current day if end_day_time is after current time"""

    query_template = 'increase(location_punctuality{%s}[%ss] offset %ss)'
    query_template, amount = create_template_labels(query_template, districts, transport_types, operators)
    # query_template, amount = query_template % ('', '%d', '%d'), 1
    now = datetime.now()
    seconds_since_midnight = (
        now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    offset = seconds_since_midnight - end_day_time
    time_range = end_day_time - start_day_time
    today = datetime.today().weekday()

    results = {}
    for day in range(period + 1):
        if offset > 0 and (today - day) % 7 in days:
            query = query_template % ((time_range, offset) * amount)
            print("amount: ", amount)
            print("query: ", query)
            result = make_prom_query(query)
            if check_json_result(result):
                data = get_data_json_result(result)
                if data:
                    for metric in data:
                        key = tuple(remove_unwanted_keys(metric['metric'], return_filters).items())
                        value = float(metric['value'][1])
                        if key in results:
                            results[key] += value
                        else:
                            results[key] = value
            else:
                print('Query to Prometheus database went wrong, status error code: %s' % (
                    result['status']))
        offset += 86400 # seconds in a day
    results = [{'metric': dict(key), 'value': value} for key, value in results.items()]
    results.sort(key=lambda x: x['value'], reverse=True)
    print(results)
    return results

def heatmap_punctuality(time, unit, vehicle_type=None):
    """Calculate percentage of metro's that is delayed."""
    transport_type_query = 'transport_type="%s"' % vehicle_type if vehicle_type else ''

    query = 'increase(location_punctuality{%s}[%s%s] offset 1d)' % (transport_type_query, time, unit)
    result = make_prom_query(query)

    lst = []
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

if __name__ == "__main__":
    print(heatmap_punctuality(1, "d", "BUS"))

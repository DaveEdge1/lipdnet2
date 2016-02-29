import csv


def read_csv_to_columns(filename):
    """
    Opens the target CSV file and creates a dictionary with one list for each CSV column.
    :param filename: (str) Filename
    :return: (dict) CSV data. Keys: Column number(int), Values: Column data (list)
    """
    d = {}
    try:
        with open(filename, 'r') as f:
            r = csv.reader(f, delimiter=',')
            # Create a dict with X lists corresponding to X columns
            for idx, col in enumerate(next(r)):
                d[idx] = []
            # Start iter through CSV data
            for row in r:
                for idx, col in enumerate(row):
                    # Append the cell to the correct column list
                    try:
                        d[idx].append(float(col))
                    except ValueError:
                        d[idx].append(col)
    except FileNotFoundError:
        print('CSV FileNotFound: ' + filename)
    return d


def write_csv_to_file(filename, d):
    """
    Writes columns of data to a target CSV file.
    :param filename: (str) Target CSV file
    :param d: (dict) A dictionary containing one list for every data column. Keys: int, Values: list
    :return: None
    """
    l_columns = []
    for k, v in d.items():
        l_columns.append(v)
    rows = zip(*l_columns)
    with open(filename, 'w+') as f:
        w = csv.writer(f)
        for row in rows:
            w.writerow(row)
    return


def add_csv_to_json(d):
    """
    Using the given paleoData dictionary from the JSON metadata, retrieve CSV data from CSV files, and insert the CSV
    data columns to their respective JSON paleoData table columns.
    :param d:
    :return:
    """
    d2 = {}
    # Loop through each table in paleoData
    for table in d:
        # Create CSV entry into dictionary that contains all columns.
        d2[table['filename']] = read_csv_to_columns(table['filename'])
        # Start putting CSV data into corresponding JSON metadata columns under 'values' key.
        for idx, col in enumerate(table['columns']):
            col['values'] = d2[table['filename']][idx]
    return d2
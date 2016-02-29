import json
import copy

import demjson

EMPTY = ['', ' ', None, 'na', 'n/a', 'nan', '?']


def write_json_to_file(filename, json_data):
    """
    Write all JSON in python dictionary to a new json file.
    :param filename: (str) Target File (name + .json)
    :param json_data: (dict) JSON data
    :return: None
    """
    # Use demjson to maintain unicode characters in output
    json_bin = demjson.encode(json_data, encoding='utf-8', compactly=False)
    # Write json to file
    try:
        open(filename, "wb").write(json_bin)
    except FileNotFoundError:
        print("Error writing json: " + filename)
    return


def read_json_from_file(filename):
    """
    Import the JSON data from target file.
    :param filename: (str) Target Files
    :return: (dict) JSON data
    """
    d = {}
    try:
        # Open json file and read in the contents. Execute DOI Resolver?
        # with open(filename, 'r') as f:
            # Load json into dictionary
        d = demjson.decode_file(filename)
    except FileNotFoundError:
        print("LiPD object: Load(). file not found")
    return d


def remove_csv_from_json(d):
    """
    Remove all CSV data 'values' entries from paleoData table in the JSON structure.
    :param d: (dict) JSON data
    :return: (dict) Metadata dictionary without CSV values
    """
    d = {}
    # Loop through each table in paleoData
    for table in d['paleoData']:
        for col in table['columns']:
            try:
                # try to delete the values key entry
                del col['values']
            except KeyError:
                # if the key doesn't exist, keep going
                print("RemoveCSVfromJSON: Error deleting values")
    return d


def remove_empty_fields(d):
    """
    Go through N number of nested data types and remove all empty entries. Recursion
    :param d: (any) Dictionary, List, or String of data
    :return: (any) Returns a same data type as original, but without empties.
    """
    # Int types don't matter. Return as-is.
    if not isinstance(d, int):
        if isinstance(d, str) or d is None:
            try:
                # Remove new line characters and carriage returns
                d = d.rstrip()
            except AttributeError:
                # None types don't matter. Keep going.
                pass
            if d in EMPTY:
                # Substitute empty entries with ""
                d = ''
        elif isinstance(d, list):
            # Recurse once for each item in the list
            for i, v in enumerate(d):
                d[i] = remove_empty_fields(d[i])
            # After substitutions, remove and empty entries.
            for i in d:
                if not i:
                    d.remove(i)
        elif isinstance(d, dict):
            # First, go through and substitute "" (empty string) entry for any values in EMPTY
            for k, v in d.items():
                d[k] = remove_empty_fields(v)
            # After substitutions, go through and delete the key-value pair.
            # This has to be done after we come back up from recursion because we cannot pass keys down.
            for key in list(d.keys()):
                if not d[key]:
                    del d[key]

    return d


def old_to_new_structure(d):
    """
    Restructure JSON to the new format. Table and columns referenced by name, not index. (dictionaries)
    :param d:(dict) JSON metadata
    :return: (dict) JSON metadata
    """
    # PaleoData dict
    tmp_p = {}

    for table in d['paleoData']:
        # All tables, all columns, table name
        tmp_t = {}
        tmp_c = {}
        t_name = table['paleoDataTableName']

        # paleoDataTableName and variableName are current
        # tableName and parameter are deprecated

        # Restructure columns into tmp_c
        for col in table['columns']:
            c_name = col['variableName']
            tmp_c[c_name] = col

        # Move table strings into tmp_t
        for k, v in table.items():
            if isinstance(v, str):
                tmp_t[k] = v

        # Move new column structure to table
        tmp_t['columns'] = copy.deepcopy(tmp_c)

        # Move table into tmp_p
        tmp_p[t_name] = copy.deepcopy(tmp_t)

    # Overwrite original paleoData dictionary with new dictionary
    d['paleoData'] = tmp_p
    return d


def new_to_old_structure(d):
    """
    Restructure JSON to the old format. Table and columns are indexed by numbers. (lists)
    :param d:(dict) JSON metadata
    :return: (dict) JSON metadata
    """
    # PaleoData dict
    tmp_p = []

    for k, v in d['paleoData'].items():
        tmp_c = []
        # For each column, append the value, forget the key.
        for i, e in v['columns'].items():
            tmp_c.append(e)
        # Replace the old column dict with the new column list
        v['columns'] = copy.deepcopy(tmp_c)
        # Append the table to the PaleoData Dict to the list, forget the key.
        tmp_p.append(v)

    # Overwrite original paleoData dictionary with new dictionary
    d['paleoData'] = tmp_p
    return d
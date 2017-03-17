from collections import deque

import numpy
import os


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def read_columns(directory, file_name):
    with open(os.path.join(directory, file_name), 'r') as file_handler:
        lines = file_handler.readlines()
        print("Lines read")
        rows = [x.strip().split(',') for x in lines]
        column_len = len(rows[0])
        columns = [None] * column_len
        print("Transforming matrix...")
        for column_index in range(len(columns)):
            columns[column_index] = [None] * len(rows)
        for row_index in range(len(rows)):
            row = rows[row_index]
            for column_index in range(len(row)):
                column = columns[column_index]
                column[row_index] = row[column_index]
        return columns


def columns_with_numbers(columns):
    i = 0
    while i < len(columns):
        is_numbers_only = True
        for cell_index in range(1, len(columns[i])):
            cell = columns[i][cell_index]
            if not is_number(cell):
                is_numbers_only = False
                break
        if is_numbers_only:
            i += 1
        else:
            del [columns[i]]
    for column_index in range(len(columns)):
        column = columns[column_index]
        for row_index in range(1, len(column)):
            column[row_index] = float(column[row_index])
    return columns


def correlations(columns):
    results = deque()
    correlation_index = 0
    for col_index_1 in range(0, len(columns)):
        column_1 = columns[col_index_1]
        title_1 = column_1[0]
        for col_index_2 in range(0, len(columns)):
            if col_index_1 == col_index_2:
                continue
            column_2 = columns[col_index_2]
            title_2 = column_2[0]
            x_set = numpy.array(column_1[1:])
            y_set = numpy.array(column_2[1:])
            linear_coefficients = numpy.polyfit(x_set, y_set, 1)
            p = numpy.poly1d(linear_coefficients)
            y_hat = p(x_set)  # or [p(z) for z in x]
            y_bar = numpy.sum(y_set) / len(y_set)  # or sum(y)/len(y)
            ss_reg = numpy.sum((y_hat - y_bar) ** 2)  # or sum([ (yihat - ybar)**2 for yihat in yhat])
            ss_tot = numpy.sum((y_set - y_bar) ** 2)  # or sum([ (yi - ybar)**2 for yi in y])
            determination = ss_reg / ss_tot
            results.append((title_1, title_2, determination))
            correlation_index += 1
    return results


def write_to_csv(directory, file_name, columns):
    with open(os.path.join(directory, file_name), 'w+') as file_handler:
        file_handler.write("\n".join([",".join([str(info) for info in row]) for row in columns]))


file_name = "20150401_20150501_3212SI005A.PV.csv"
write_file_name = "correlations_" + file_name
print("Reading columns...")
columns = read_columns("./", file_name)
print("Filtering columns to numeric data only...")
columns = columns_with_numbers(columns)
print("Calculating correlations")
results = correlations(columns)
print(results)
write_to_csv("./", write_file_name, results)
print("Written to " + write_file_name)

from collections import deque

import numpy
import os
import unicodedata


def to_number(s):
    if s is None:
        return -10000
    try:
        return float(s)
    except ValueError:
        pass
    return -10000


def read_columns(directory, file_name):
    with open(os.path.join(directory, file_name), 'r') as file_handler:
        lines = file_handler.readlines()
        print("Lines read")
        rows = (x.strip().split(',') for x in lines)
        column_len = len(lines[0].strip().split(','))
        print("Creating columns")
        columns = [None] * column_len
        print("Creating rows")
        for column_index in range(len(columns)):
            columns[column_index] = [None] * len(lines)
        print("Transforming matrix...")
        row_index = 0
        for row in rows:
            for column_index in range(len(row)):
                if column_index >= column_len:
                    print("Warning, column index was %s and column count was %s" % (column_index, column_len))
                    continue
                column = columns[column_index]
                column[row_index] = row[column_index]
            row_index += 1
        return columns


def columns_with_numbers(columns):
    i = len(columns) - 1
    while i >= 0:
        print("Processing: %s" % i)
        for cell_index in range(1, len(columns[i])):
            columns[i][cell_index] = to_number(columns[i][cell_index])
        i -= 1
    return columns


def calc_bad_grid(columns):
    bad_grid = [None] * len(columns)
    for c in range(len(columns)):
        bad_column_indexes = set()
        column = columns[c]
        for r in range(len(column) - 1, -1, -1):
            cell = column[r]
            if cell is None:
                bad_column_indexes.add(r)
        bad_grid[c] = bad_column_indexes
    return bad_grid


def correlations(columns, bad_grid):
    results = deque()
    results.append(["x axis", "y axis", "Determination (R squared)", "Gradient", "Y Translation"])
    correlation_index = 0
    for col_index_1 in range(0, len(columns)):
        column_1 = columns[col_index_1]
        title_1 = column_1[0]
        bad_indexes_1 = bad_grid[col_index_1]
        if len(column_1) - len(bad_indexes_1) <= 3:
            #print("Column 1 too few data entries, skipping")
            continue
        print(col_index_1)
        for col_index_2 in range(0, len(columns)):
            if col_index_1 == col_index_2:
                continue
            #print("Correlating %s and %s" % (col_index_1, col_index_2))
            column_2 = columns[col_index_2]
            bad_indexes_2 = bad_grid[col_index_2]
            title_2 = column_2[0]
            data_set_1 = deque()
            data_set_2 = deque()
            r = 1
            combined_set = bad_indexes_1 | bad_indexes_2
            if len(column_1) - len(combined_set) <= 3:
                print("data set is too small: %s" % len(combined_set))
                continue
            while r < len(column_2) and r < len(column_1):
                if r in combined_set:
                    pass
                else:
                    data_set_1.append(column_1[r])
                    data_set_2.append(column_2[r])
                r += 1
            x_set = numpy.array(column_1[1:])
            y_set = numpy.array(column_2[1:])
            linear_coefficients = numpy.polyfit(x_set, y_set, 1)
            p = numpy.poly1d(linear_coefficients)
            y_hat = p(x_set)  # or [p(z) for z in x]
            y_bar = numpy.sum(y_set) / len(y_set)  # or sum(y)/len(y)
            ss_tot = numpy.sum((y_set - y_bar) ** 2)  # or sum([ (yi - ybar)**2 for yi in y])
            ss_reg = numpy.sum((y_hat - y_bar) ** 2)  # or sum([ (yihat - ybar)**2 for yihat in yhat])
            determination = ss_reg / ss_tot
            results.append((title_1, title_2, determination, linear_coefficients[0], linear_coefficients[1]))
            correlation_index += 1
    return results


def write_to_csv(directory, file_name, columns):
    with open(os.path.join(directory, file_name), 'w+') as file_handler:
        file_handler.write("\n".join([",".join([str(info) if info is not None else "NULL" for info in row]) for row in
                                      columns] if columns is not None else "NULL"))


directory = "../pats-data/"
file_name = "20160101_20160201_3212SI005A.PV.csv"
write_file_name = "correlations_" + file_name
print("Reading columns...")
columns = read_columns(directory, file_name)
print("Parsing to floats...")
columns = columns_with_numbers(columns)
print("Finding bad indexes")
bad_grid = calc_bad_grid(columns)
print("Calculating correlations")
results = correlations(columns, bad_grid)
print(results)
write_to_csv(directory, write_file_name, results)
print("Written to " + write_file_name)

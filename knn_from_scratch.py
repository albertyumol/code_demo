# -*- coding: utf-8 -*-

"""K-Nearest Neighbor Algorithm From Scratch.

KNN predicts a target variable based on feature variables. 
The algorithm requires a training set to use for prediction. 
The prediction will be done by looking into K number of 
nearest neighbors in the training set, and get the mode 
(if classifier) or mean (if regression).

Input of this script is the training data (X_train.csv),
data with missing values (X_impute.csv), and output file
name (test_output.csv).

To run: `python knn_from_scratch.py -i X_impute.csv -t X_train.csv -o test_output.csv`
"""


#Import python libraries
import math
import numpy as np
import statistics
import logging
from datetime import datetime
import argparse
import textwrap
import pandas as pd
import os

def euclidean(X1, X2):
	"""
	Calculates the euclidean distance between two matrices.

	:param X1: An n-dimentional matrix.
	:param X2: An n-dimentional matrix.
	:return: Euclidean distance.
	"""
	if len(X1) != len(X2):
		raise ValueError("Lengths of instances must be equal!")
	distance = 0
	for i in range(len(X1)):
		distance += (X2[i] - X1[i]) **2
	return math.sqrt(distance)


def getkneighbors(train, test, k):
	"""
	Identify the k number of neighbors from the train set for each row in the set.
	:param train: Iterable of feature.
	:param test: Iterable of feature.
	:return: List of k indixes for each in the test set.
	"""
	neighbors = []
	for i in range(len(test)):
		distanceDict = {}
		closest_neighbors = []
		for j in range(len(train)):
			distanceDict[j] = euclidean(test[i], train[j])
		distanceDict = dict(sorted(distanceDict.items(), key = lambda item: item[1]))
		closest_neighbors += distanceDict.keys()
		closest_neighbors = closest_neighbors[:k]
		neighbors.append(closest_neighbors)
	return neighbors


def predictknn(train, neighbors, method):
    '''
    Get the prediction by mode or mean of train target values if classification or regression. 
    
    :param train: Iterable of targets.
    :param neighbors: Output of `getkneighbors()`.
    :param method: mode for KNN, "classification" or "regression".
    :return: List of predictions for each test value.
    '''
    predictions = []
    
    if method == 'classification':
        _method = statistics.mode
    elif method == 'regression':
        _method = statistics.mean
    else:
        raise ValueError('Invalid method.')
        
    for i_test in neighbors:
        predictions.append(_method([train[i_neighbor] for i_neighbor in i_test]))
    
    return predictions


def KNN_train_predict(X_train, y_train, X_test, K, method):
	'''
	Consolidates previous all above functions.
	'''
	return predictknn(y_train, getkneighbors(X_train, X_test, K), method)


def main():

	#Create logging file system
	log_dir = os.path.join(os.getcwd() + os.sep, 'logs' + os.sep)
	try:
		os.mkdir(log_dir)
	except:
		pass
	logging.basicConfig(filename=log_dir+datetime.now().strftime('log_%H_%M_%d_%m_%Y.log'), level=logging.INFO)
	logging.info('Started')

	#Create parser for input/output in terminal
	parser = argparse.ArgumentParser(prog='Replacing Null values through Regression', 
		formatter_class=argparse.RawDescriptionHelpFormatter, 
		description=textwrap.dedent('''\
	Imputing Null Values in a Column through KNN
	---------------------------------------------------------
	This code implements KNN as a regression operation to
	impute missing values in a feature column.
	'''),
	epilog="Developed by Albert Yumol.")
	parser.add_argument('-d', '--debug', help='Debugging output', action='store_true')
	parser.add_argument('-i', '--input', type=argparse.FileType('r'), required=True,
		help='Input csv file')
	parser.add_argument('-t', '--train', type=argparse.FileType('r'), required=True,
		help='Train data file')
	parser.add_argument('-o', '--output', type=argparse.FileType('w'), required=True,
		help='Output csv file')
	args = vars(parser.parse_args())
	logging.info('Trying to open csv file...')

	#Read parsed files from terminal
	try:
		X_impute = pd.read_csv(args["input"], index_col = 0).values.tolist()
		X_train = pd.read_csv(args["train"], index_col = 0).values.tolist()
	except Exception as e:
		logging.exception(str(e))

	#Isolate rows with null values
	X_test = [y for y in X_impute if np.any(np.isnan(y)) == True]

	#Extract the label column
	y_train = [y[2] for y in X_train]

	#Drop label columns for training sets
	X_train = [list(np.delete(y, [2])) for y in X_train]
	X_test = [list(np.delete(y, [2])) for y in X_test]

	#Run KNN regression
	nearest_neighbor = 2
	predict_y_test = KNN_train_predict(X_train, y_train, X_test, nearest_neighbor, "regression")
	predict_y_test = np.round(predict_y_test, decimals = 1)

	#Replace nulls with values from prediction
	for i in predict_y_test:
		for j in X_impute:
			if np.isnan(j[2]) == True:
				j[2] = i
				break

	#Store value in csv
	X_impute = pd.DataFrame(X_impute)
	X_impute.to_csv(args['output'].name)

	logging.info('Finished')
	logging.info('Success!')

if __name__ == '__main__':
	main()
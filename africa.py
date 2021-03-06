import pandas as pd
import numpy as np
import math
import time
import os.path
from sklearn import svm, cross_validation
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import make_scorer
import sys
import sklearn.feature_selection 

def mcrmseEvaluate(y, yhat):
	mcrmse1 = np.sqrt(np.sum((y - yhat)**2)/len(y))
	return mcrmse1

start = time.time()

train = pd.read_csv('training.csv')
test = pd.read_csv('sorted_test.csv')

CVFile = 'solution/africa_prediction#'
num=1

while os.path.isfile(CVFile + str(num) + ".csv"):
	num += 1

AfricaCVFile = 'solution/africa_CV#' + str(num) + '.txt'
PredictionFile = 'solution/africa_prediction#' + str(num) + '.csv'
PredictionTrainFile = 'solution/africa_prediction_train#' + str(num) + '.csv'

labels = train[['Ca','P','pH','SOC','Sand']].values

train.drop(['Ca', 'P', 'pH', 'SOC', 'Sand', 'PIDN'], axis=1, inplace=True)
test.drop('PIDN', axis=1, inplace=True)
cnames=['Ca', 'P', 'pH', 'SOC', 'Sand']
train['Depth1'] = train['Depth'].map(lambda x: 1 if x == 'Topsoil' else 0).astype(float)
test['Depth1'] = test['Depth'].map(lambda x: 1 if x == 'Topsoil' else 0).astype(float)
train.drop('Depth', axis=1, inplace=True)
test.drop('Depth', axis=1, inplace=True)

train.drop(['BSAN', 'BSAS', 'BSAV', 'CTI', 'ELEV', 'EVI', 'LSTD', 'LSTN', 'REF1', 'REF2', 'REF3', 'REF7', 'RELI', 'TMAP', 'TMFI'], axis=1, inplace=True)
test.drop(['BSAN', 'BSAS', 'BSAV', 'CTI', 'ELEV', 'EVI', 'LSTD', 'LSTN', 'REF1', 'REF2', 'REF3', 'REF7', 'RELI', 'TMAP', 'TMFI'], axis=1, inplace=True)
#train.drop(["m2379.76", "m2377.83", "m2375.9",  "m2373.97", "m2372.04", "m2370.11", "m2368.18", "m2366.26", "m2364.33", "m2362.4",  "m2360.47", "m2358.54", "m2356.61", "m2354.68", "m2352.76"], axis=1, inplace=True)
#test.drop(["m2379.76", "m2377.83", "m2375.9",  "m2373.97", "m2372.04", "m2370.11", "m2368.18", "m2366.26", "m2364.33", "m2362.4",  "m2360.47", "m2358.54", "m2356.61", "m2354.68", "m2352.76"], axis=1, inplace=True)

xtrain, xtest = np.array(train)[:,:], np.array(test)[:,:]

xtrain1, xtest1 = np.array(train)[:,:], np.array(test)[:,:]

nrow1 = xtrain1.shape[0]
ncol = xtrain1.shape[1]
nrow2 = xtest1.shape[0]
xtrain = xtrain1.copy()
xtest = xtest1.copy()
xtrain.resize(nrow1, ncol*2)
xtest.resize(nrow2, ncol*2)

xtrain[:nrow1,:ncol] = xtrain1
xtest[:nrow2,:ncol] = xtest1

#print xtrain.shape
#print xtest.shape

for i in range(ncol):
	xtrain[:,ncol + i] = xtrain[:,i]*xtrain[:,i]
	xtest[:,ncol + i] = xtest[:,i]*xtest[:,i]

sup_vec = svm.SVR(C=1000, verbose = 2, tol=0.0001, epsilon=0.001, random_state = 512)
sup_vec1 = svm.SVR(C=100, verbose = 2, tol=0.0001, epsilon=0.001, random_state = 512) 
sup_vec2 = svm.SVR(C=10000, verbose = 2, tol=0.0001, epsilon=0.001, random_state = 512)
sup_vec3 = svm.SVR(C=5000, verbose = 2, tol=0.0001, epsilon=0.001, random_state = 512)
sup_vec4 = svm.SVR(C=100, verbose = 2, tol=0.0001, epsilon=0.001, random_state = 512)

output = open(AfricaCVFile,'w')
output.close()
preds = np.zeros((xtest.shape[0], 5))
predsXTrain = np.zeros((xtrain.shape[0], 5))
mcrmse = 0
mcrmseALL = 0
mcrmseSCORE = 0

xtrain=xtrain.astype(float)
xtest=xtest.astype(float)

xtrain_scaled = xtrain
xtest_scaled = xtest

scorer = make_scorer(mcrmseEvaluate)

for i in range(5):
	print("Predicting variable: " + cnames[i])
	output = open(AfricaCVFile,'a')
	output.write("Predicting variable: " + cnames[i] + '\n')
	output.close()
	xtrain_scaled = xtrain_scaled if i == 1 else xtrain
	xtest_scaled = xtest_scaled if i == 1 else xtest
	if i == 1:
		scores = cross_validation.cross_val_score(sup_vec1, xtrain_scaled, labels[:, i], cv=cross_validation.ShuffleSplit(xtrain_scaled.shape[0], test_size=0.6, random_state=512), scoring=scorer, n_jobs=-1, pre_dispatch = 'all')
	elif i == 2:
		scores = cross_validation.cross_val_score(sup_vec2, xtrain_scaled, labels[:, i], cv=cross_validation.ShuffleSplit(xtrain_scaled.shape[0], test_size=0.6, random_state=512), scoring=scorer, n_jobs=-1, pre_dispatch = 'all')
	elif i == 3:
		scores = cross_validation.cross_val_score(sup_vec3, xtrain_scaled, labels[:, i], cv=cross_validation.ShuffleSplit(xtrain_scaled.shape[0], test_size=0.6, random_state=512), scoring=scorer, n_jobs=-1, pre_dispatch = 'all')
	elif i == 4:
		scores = cross_validation.cross_val_score(sup_vec4, xtrain_scaled, labels[:, i], cv=cross_validation.ShuffleSplit(xtrain_scaled.shape[0], test_size=0.6, random_state=512), scoring=scorer, n_jobs=-1, pre_dispatch = 'all')
	else:
		scores = cross_validation.cross_val_score(sup_vec, xtrain_scaled, labels[:, i], cv=cross_validation.ShuffleSplit(xtrain_scaled.shape[0], test_size=0.6, random_state=512), scoring=scorer, n_jobs=-1, pre_dispatch = 'all')
	#print scores
	
	if i == 1:
		sup_vec1.fit(xtrain_scaled, labels[:,i])
		preds[:,i] = sup_vec1.predict(xtest_scaled).astype(float)
		predsXTrain[:,i] = sup_vec1.predict(xtrain_scaled).astype(float)
	if i == 2:
		sup_vec2.fit(xtrain_scaled, labels[:,i])
		preds[:,i] = sup_vec2.predict(xtest_scaled).astype(float)
		predsXTrain[:,i] = sup_vec2.predict(xtrain_scaled).astype(float)
	if i == 3:
		sup_vec3.fit(xtrain_scaled, labels[:,i])
		preds[:,i] = sup_vec3.predict(xtest_scaled).astype(float)
		predsXTrain[:,i] = sup_vec3.predict(xtrain_scaled).astype(float)
	if i == 4:
		sup_vec4.fit(xtrain_scaled, labels[:,i])
		preds[:,i] = sup_vec4.predict(xtest_scaled).astype(float)
		predsXTrain[:,i] = sup_vec4.predict(xtrain_scaled).astype(float)
	else:
		sup_vec.fit(xtrain_scaled, labels[:,i])
		preds[:,i] = sup_vec.predict(xtest_scaled).astype(float)
		predsXTrain[:,i] = sup_vec.predict(xtrain_scaled).astype(float)
	
	cv = cross_validation.KFold(len(xtrain_scaled), n_folds=10, indices=False, random_state = 512)
	
	results = []
	for traincv, testcv in cv:
		if i == 1:
			probas = sup_vec1.fit(xtrain_scaled[traincv], labels[traincv, i]).predict(xtrain_scaled[testcv]).astype(float)
		if i == 2:
			probas = sup_vec2.fit(xtrain_scaled[traincv], labels[traincv, i]).predict(xtrain_scaled[testcv]).astype(float)
		if i == 3:
			probas = sup_vec3.fit(xtrain_scaled[traincv], labels[traincv, i]).predict(xtrain_scaled[testcv]).astype(float)
		if i == 4:
			probas = sup_vec4.fit(xtrain_scaled[traincv], labels[traincv, i]).predict(xtrain_scaled[testcv]).astype(float)
		else:
			probas = sup_vec.fit(xtrain_scaled[traincv], labels[traincv, i]).predict(xtrain_scaled[testcv]).astype(float)
		results.append(mcrmseEvaluate(labels[testcv, i], probas))
	
	mcrmse1 = np.array(results).mean()
	mcrmse2 = mcrmseEvaluate(predsXTrain[:,i], labels[:,i])
	mcrmse3 = scores.mean()

	output = open(AfricaCVFile,'a')
	output.write("MCRMSE: " + str(mcrmse1) + '\n')
	print("MCRMSE: " + str(mcrmse1) + '\n')
	output.write("mcrmseALL " + str(mcrmse2) + '\n')
	print("mcrmseALL " + str(mcrmse2) + '\n')
	output.write("mcrmseSCORE " + str(mcrmse3) + '\n')
	print("mcrmseSCORE " + str(mcrmse3) + '\n')
	output.close()

	mcrmse += mcrmse1
	mcrmseALL += mcrmse2
	mcrmseSCORE += mcrmse3

output = open(AfricaCVFile,'a')
output.write("Total MCRMSE " + str(mcrmse/5) + '\n')
output.write("Total MCRMSEALL " + str(mcrmseALL/5) + '\n')
output.write("Total MCRMSESCOREALL " + str(mcrmseSCORE/5) + '\n')
print("Total MCRMSE " + str(mcrmse/5) + '\n')
print("Total MCRMSEALL " + str(mcrmseALL/5) + '\n')
print("Total MCRMSESCOREALL " + str(mcrmseSCORE/5) + '\n')

sample = pd.read_csv('solution/sample_submission.csv')
sample['Ca'] = preds[:,0]
sample['P'] = preds[:,1]
sample['pH'] = preds[:,2]
sample['SOC'] = preds[:,3]
sample['Sand'] = preds[:,4]
sample.to_csv(PredictionFile, index = False)

sample = pd.read_csv('solution/sample_submission_train.csv')
sample['Ca'] = predsXTrain[:,0]
sample['P'] = predsXTrain[:,1]
sample['pH'] = predsXTrain[:,2]
sample['SOC'] = predsXTrain[:,3]
sample['Sand'] = predsXTrain[:,4]
sample.to_csv(PredictionTrainFile, index = False)

end = time.time()
print("Total time(min): " + str((end - start)/60))
output.write("Total time(min): " + str((end - start)/60))

output.close()








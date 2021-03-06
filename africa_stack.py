import pandas as pd
import numpy as np
import time
import os.path
from sklearn.ensemble import RandomForestRegressor
from sklearn import svm, cross_validation
from sklearn import preprocessing
from sklearn.metrics import make_scorer
from joblib import Parallel, delayed

def mcrmseEvaluate(y, yhat):
    mcrmse1 = np.sqrt(np.sum((y - yhat)**2)/len(y))
    return mcrmse1

start = time.time()

train = pd.read_csv('training.csv')
test = pd.read_csv('sorted_test.csv')

CVFile = 'solution/africa_stack_prediction#'
num=1

while os.path.isfile(CVFile + str(num) + ".csv"):
  num += 1

AfricaCVFile = 'solution/africa_stack_CV#' + str(num) + '.txt'
PredictionFile = 'solution/africa_stack_prediction#' + str(num) + '.csv'
PredictionTrainFile = 'solution/africa_stack_prediction_train#' + str(num) + '.csv'

labels = train[['Ca','P','pH','SOC','Sand']].values

train.drop(['Ca', 'P', 'pH', 'SOC', 'Sand', 'PIDN'], axis=1, inplace=True)
test.drop('PIDN', axis=1, inplace=True)
cnames=['Ca', 'P', 'pH', 'SOC', 'Sand']
train['Depth1'] = train['Depth'].map(lambda x: 1 if x == 'Topsoil' else 0).astype(float)
test['Depth1'] = test['Depth'].map(lambda x: 1 if x == 'Topsoil' else 0).astype(float)

train.drop(['BSAN', 'BSAS', 'BSAV', 'CTI', 'ELEV', 'EVI', 'LSTD', 'LSTN', 'REF1', 'REF2', 'REF3', 'REF7', 'RELI', 'TMAP', 'TMFI', 'Depth'], axis=1, inplace=True)
test.drop(['BSAN', 'BSAS', 'BSAV', 'CTI', 'ELEV', 'EVI', 'LSTD', 'LSTN', 'REF1', 'REF2', 'REF3', 'REF7', 'RELI', 'TMAP', 'TMFI', 'Depth'], axis=1, inplace=True)
train.drop(["m2379.76", "m2377.83", "m2375.9",  "m2373.97", "m2372.04", "m2370.11", "m2368.18", "m2366.26", "m2364.33", "m2362.4",  "m2360.47", "m2358.54", "m2356.61", "m2354.68", "m2352.76"], axis=1, inplace=True)
test.drop(["m2379.76", "m2377.83", "m2375.9",  "m2373.97", "m2372.04", "m2370.11", "m2368.18", "m2366.26", "m2364.33", "m2362.4",  "m2360.47", "m2358.54", "m2356.61", "m2354.68", "m2352.76"], axis=1, inplace=True)

xtrain, xtest = np.array(train)[:,:], np.array(test)[:,:]

sup_vec = svm.SVR(C=1000, verbose = 2, tol=0.0001, epsilon = 0.001, random_state = 512)
sup_vec1 = svm.SVR(C=100, verbose = 2, tol=0.0001, epsilon = 0.001, random_state = 512) 
sup_vec2 = svm.SVR(C=10000, verbose = 2, tol=0.0001, epsilon = 0.001, random_state = 512)
sup_vec3 = svm.SVR(C=5000, verbose = 2, tol=0.0001, epsilon = 0.001, random_state = 512)
sup_vec4 = svm.SVR(C=100, verbose = 2, tol=0.0001, epsilon = 0.001, random_state = 512)

rf = RandomForestRegressor(n_estimators=20, n_jobs=-1, random_state = 512)

output = open(AfricaCVFile,'w')
output.close()
xtrain=xtrain.astype(float)
xtest=xtest.astype(float)

xtrain_scaled = preprocessing.scale(xtrain)
xtest_scaled = preprocessing.scale(xtest)
X_dev = xtrain_scaled
X_test = xtest_scaled

scorer = make_scorer(mcrmseEvaluate)
    
n_trees = 10
n_folds = 5

clfs = [rf,sup_vec,sup_vec1,sup_vec2,sup_vec3,sup_vec4]

blend_train = np.zeros((X_dev.shape[0], len(clfs))) # Number of training data x Number of classifiers
blend_test = np.zeros((X_test.shape[0], len(clfs))) # Number of testing data x Number of classifiers

print 'X_test.shape = %s' % (str(X_test.shape))
print 'blend_train.shape = %s' % (str(blend_train.shape))
print 'blend_test.shape = %s' % (str(blend_test.shape))

cnames=['Ca', 'P', 'pH', 'SOC', 'Sand']
mcrmseScore=0
mcrmseStackCV_ALL = 0
predictions = np.zeros((xtest.shape[0], 5))
predsXTrain = np.zeros((xtrain.shape[0], 5))

for k in range(5):
  print "Predicting variable: " + cnames[k]
  output = open(AfricaCVFile,'a')
  output.write("Predicting variable: " + cnames[k] + '\n')
  output.close()
  Y_dev = labels[:, k]
  
  skf = list(cross_validation.KFold(len(X_dev), n_folds=10, indices=False, random_state = 512))

  for j, clf in enumerate(clfs):
    print cnames[k] + ' - Training classifier [%s]' % (j)
    blend_test_j = np.zeros((X_test.shape[0], len(skf))) 
    for i, (train_index, cv_index) in enumerate(skf):
      print '      Fold [%s]' % (i)
      
      X_train = X_dev[train_index]
      Y_train = Y_dev[train_index]
      X_cv = X_dev[cv_index]
      Y_cv = Y_dev[cv_index]
      
      clf.fit(X_train, Y_train)
      
      blend_train[cv_index, j] = clf.predict(X_cv)
      blend_test_j[:, i] = clf.predict(X_test)
    blend_test[:, j] = blend_test_j.mean(1)

  print '   Y_dev.shape = %s' % (Y_dev.shape)

  if k ==1:
    bclf = sup_vec1
  if k ==2:
    bclf = sup_vec2
  if k ==3:
    bclf = sup_vec3
  if k ==4:
    bclf = sup_vec4
  else:
    bclf = sup_vec

  cv = cross_validation.KFold(len(X_dev), n_folds=10, indices=False, random_state = 54321)
  results = []
  for traincv, testcv in cv:
    probas = bclf.fit(X_dev[traincv], labels[traincv, k]).predict(X_dev[testcv]).astype(float)
    results.append(mcrmseEvaluate(labels[testcv, k], probas))
  
  bclf.fit(blend_train, Y_dev)

  output = open(AfricaCVFile,'a')
  mcrmseStackCV = np.array(results).mean()
  output.write("mcrmseStackCV: " + str(mcrmseStackCV) + '\n')
  print("mcrmseStackCV: " + str(mcrmseStackCV) + '\n')
  mcrmseStackCV_ALL += mcrmseStackCV/5

  predictions[:,k] = bclf.predict(blend_test) 
  predsXTrain[:,k] = bclf.predict(blend_train)
  Y_train_predict = predsXTrain[:,k]
  score = mcrmseEvaluate(Y_dev, Y_train_predict)
  print 'mcrmse = %s' % (score)
  output.write("Predicting variable: " + cnames[k] + ' mcrmse = ' + str(score) + '\n')
  output.close()
  mcrmseScore += score/5
  
print 'Total MCRMSE = %s' % (mcrmseScore)
print 'Total MCRMSE STACK CV = %s' % (mcrmseStackCV_ALL)

output = open(AfricaCVFile,'a')
output.write("Total MCRMSE " + str(mcrmseScore) + '\n')
output.write("Total MCRMSE STACK CV " + str(mcrmseStackCV_ALL) + '\n')

sample = pd.read_csv('solution/sample_submission.csv')
sample['Ca'] = predictions[:,0]
sample['P'] = predictions[:,1]
sample['pH'] = predictions[:,2]
sample['SOC'] = predictions[:,3]
sample['Sand'] = predictions[:,4]
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

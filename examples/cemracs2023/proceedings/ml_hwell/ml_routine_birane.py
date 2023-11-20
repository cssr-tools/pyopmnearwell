# Modified from https://machinelearningmastery.com/time-series-prediction-with-deep-learning-in-python-with-keras/
import numpy as np
import matplotlib.pyplot as plt
import math
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import MinMaxScaler

tf.keras.utils.set_random_seed(42)

TDATA = 800  #Time in days for the ML routines (the rest (for data times greater that this) is used for the assessment of the NN trained models)
train_data_frac = 0.7 # Fraction of the data used for the training of the NN
look_back = 42 #Size of the window

# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back):
		a = dataset[i:(i+look_back)]
		dataX.append(a)
		dataY.append(dataset[i + look_back])
	return np.array(dataX), np.array(dataY)

# load the dataset
x_all = np.load('times.npy')
x_sort_indx = np.argsort(x_all)
y0_all = np.load('fgpt.npy')[x_sort_indx].reshape(-1, 1)
y1_all = np.load('fgit.npy')[x_sort_indx].reshape(-1, 1)
y0 = np.load('fgpt.npy')[x_sort_indx]
y1 = np.load('fgit.npy')[x_sort_indx]
x_all = x_all[x_sort_indx].reshape(-1, 1)
scale_y0 = MinMaxScaler()
scale_y1 = MinMaxScaler()
y0_scaled = scale_y0.fit_transform(y0_all)
y1_scaled = scale_y1.fit_transform(y1_all)
x0 = x_all[x_all < TDATA] # Keep only the data before the assessment
y0 = scale_y0.transform(y0_all[x_all < TDATA].reshape(-1, 1)).squeeze() # Keep only the data before the assessment
y1 = scale_y1.transform(y1_all[x_all < TDATA].reshape(-1, 1)).squeeze() # Keep only the data before the assessment
# split into train and test sets
train_size = math.floor(len(x0) * train_data_frac)
train0, test0, forecast0 = y0[:train_size], y0[train_size-look_back:], scale_y0.transform(y0_all[len(x0)-look_back:].reshape(-1, 1)).squeeze()
train1, test1, forecast1 = y1[:train_size], y1[train_size-look_back:], scale_y1.transform(y1_all[len(x0)-look_back:].reshape(-1, 1)).squeeze()
# reshape dataset
trainX0, trainY0 = create_dataset(train0, look_back)
validationX0, validationY0 = create_dataset(test0, look_back)
forecastX0, forecastY0 = create_dataset(forecast0, look_back)
trainX1, trainY1 = create_dataset(train1, look_back)
validationX1, validationY1 = create_dataset(test1, look_back)
forecastX1, forecastY1 = create_dataset(forecast1, look_back)
train_dataset0 = tf.data.Dataset.from_tensor_slices((trainX0, trainY0))
val_dataset0 = tf.data.Dataset.from_tensor_slices((validationX0, validationY0))
train_dataset1 = tf.data.Dataset.from_tensor_slices((trainX1, trainY1))
val_dataset1 = tf.data.Dataset.from_tensor_slices((validationX1, validationY1))
train_dataset0 = train_dataset0.batch(2)
val_dataset0 = val_dataset0.batch(2)
train_dataset1 = train_dataset1.batch(2)
val_dataset1 = val_dataset1.batch(2)
# create and fit the model
# model0 = Sequential()
# model0.add(Dense(8, input_shape=(look_back,), activation='relu'))
# model0.add(Dense(8, activation='relu'))
# model0.add(Dense(1))
# model0.compile(loss='mean_squared_error', optimizer='Nadam')
# model0.fit(train_dataset0, epochs=2000, verbose=2, validation_data=val_dataset0)
# model1 = Sequential()
# model1.add(Dense(8, input_shape=(look_back,), activation='relu'))
# model1.add(Dense(8, activation='relu'))
# model1.add(Dense(1))
# model1.compile(loss='mean_squared_error', optimizer='RMSprop')
# model1.fit(train_dataset1, epochs=2000, verbose=2, validation_data=val_dataset1)

# create and fit the model
optimchoice = tf.keras.optimizers.legacy.Nadam(lr=0.0007, beta_1=0.9, beta_2=0.65, epsilon=1e-9)
optimchoice2 = tf.keras.optimizers.legacy.RMSprop(lr=0.0007, rho=0.95, epsilon=1e-8, decay=0.0005)
# optimchoice2 = tf.keras.optimizers.legacy.Nadam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
# optimchoice = tf.keras.optimizers.SGD(lr=0.001, momentum=0.1, nesterov=False)
model0 = Sequential()
model0.add(Dense(3, input_shape=(look_back,), activation='relu'))
model0.add(Dense(1, activation='relu'))
model0.add(Dense(1))
model0.compile(loss='mean_squared_error', optimizer=optimchoice)
model0.fit(train_dataset0, epochs=2000, verbose=2, validation_data=val_dataset0)
model1 = Sequential()
model1.add(Dense(11, input_shape=(look_back,), activation='relu'))
# model1.add(Dense(8, activation='relu'))
model1.add(Dense(8, activation='relu'))
model1.add(Dense(1))
model1.compile(loss='mean_squared_error', optimizer=optimchoice2)
model1.fit(train_dataset1, epochs=2000, verbose=2, validation_data=val_dataset1)

# has context menu
# Compose
# generate predictions for training
trainPredict0 = model0.predict(trainX0)
testPredict0 = model0.predict(validationX0)
testForecast0 = model0.predict(forecastX0)
mlEvaluation0 = []
for i in range(look_back):
	mlEvaluation0.append(testPredict0[-look_back + i][0])
for _ in range(len(x_all[len(x0):])):
	inputData = []
	for i in range(look_back):
		inputData.append(mlEvaluation0[-look_back + i])
	mlEvaluation0.append(model0.predict(np.array([inputData]).reshape(1,look_back))[0][0])
mlEvaluation0 = scale_y0.inverse_transform(np.array(mlEvaluation0).reshape(-1, 1)).squeeze()
trainPredict0 = scale_y0.inverse_transform(trainPredict0)
testPredict0 = scale_y0.inverse_transform(testPredict0)
testForecast0 = scale_y0.inverse_transform(testForecast0)
trainPredict1 = model1.predict(trainX1)
testPredict1 = model1.predict(validationX1)
testForecast1 = model1.predict(forecastX1)
mlEvaluation1 = []
for i in range(look_back):
	mlEvaluation1.append(testPredict1[-look_back + i][0])
for _ in range(len(x_all[len(x0):])):
	inputData = []
	for i in range(look_back):
		inputData.append(mlEvaluation1[-look_back + i])
	mlEvaluation1.append(model1.predict(np.array([inputData]).reshape(1,look_back))[0][0])
mlEvaluation1 = scale_y1.inverse_transform(np.array(mlEvaluation1).reshape(-1, 1)).squeeze()
trainPredict1 = scale_y1.inverse_transform(trainPredict1)
testPredict1 = scale_y1.inverse_transform(testPredict1)
testForecast1 = scale_y1.inverse_transform(testForecast1)
# plot baseline and predictions
plt.plot(x_all, y0_all, label="Data", linestyle='', marker = '*')
plt.plot(x0[look_back:len(trainPredict0)+look_back], trainPredict0, label="ML train")
plt.plot(x0[len(trainPredict0)+look_back:], testPredict0, label="ML validation")
plt.plot(x_all[len(x0):], testForecast0, label="ML forecast (input data from simulations)")
plt.plot(x_all[len(x0):], mlEvaluation0[look_back:], label="ML forecast (input data from ML prediciton)")
plt.ylabel(r"Produced H$_2$ [sm${^3}$]")
plt.xlabel(r"Days [#]")
plt.axvline(x = x0[len(trainPredict0)+look_back], linestyle='dotted', color = 'k')
plt.axvline(x = TDATA, linestyle='dotted', color = 'k')
plt.legend()
plt.savefig("ml_fgpt.png", dpi=1200)
plt.close()

plt.plot(x_all, y1_all, label="Data", linestyle='', marker = '*')
plt.plot(x0[look_back:len(trainPredict1)+look_back], trainPredict1, label="ML train")
plt.plot(x0[len(trainPredict1)+look_back:], testPredict1, label="ML validation")
plt.plot(x_all[len(x0):], testForecast1, label="ML forecast (input data from simulations)")
plt.plot(x_all[len(x0):], mlEvaluation1[look_back:], label="ML forecast (input data from ML prediciton)")
plt.ylabel(r"Injected H$_2$ [sm${^3}$]")
plt.xlabel(r"Days [#]")
plt.axvline(x = x0[len(trainPredict1)+look_back], linestyle='dotted', color = 'k')
plt.axvline(x = TDATA, linestyle='dotted', color = 'k')
plt.legend()
plt.savefig("ml_fgit.png", dpi=1200)
plt.close()

plt.plot(x_all, y1_all - y0_all, label="Data", linestyle='', marker = '*')
plt.plot(x0[look_back:len(trainPredict1)+look_back], trainPredict1 - trainPredict0, label="ML train")
plt.plot(x0[len(trainPredict1)+look_back:], testPredict1 - testPredict0, label="ML validation")
plt.plot(x_all[len(x0):], testForecast1 - testForecast0, label="ML forecast (input data from simulations)")
plt.plot(x_all[len(x0):], mlEvaluation1[look_back:] - mlEvaluation0[look_back:], label="ML forecast (input data from ML prediciton)")
plt.ylabel(r"Injected - produced H$_2$ [sm${^3}$]")
plt.xlabel(r"Days [#]")
plt.axvline(x = x0[len(trainPredict1)+look_back], linestyle='dotted', color = 'k')
plt.axvline(x = TDATA, linestyle='dotted', color = 'k')
plt.legend()
plt.savefig("ml_fgit_fgpt.png", dpi=1200)
plt.close()

plt.plot(x_all, y0_all / np.clip(y1_all, 1e-10, None), label="Data", linestyle='', marker = '*')
plt.plot(x0[look_back:len(trainPredict1)+look_back], trainPredict0 /np.clip(trainPredict1, 1e-10, None) , label="ML train")
plt.plot(x0[len(trainPredict1)+look_back:], testPredict0 / np.clip(testPredict0, 1e-10, None), label="ML validation")
plt.plot(x_all[len(x0):], testForecast0 / np.clip(testForecast1, 1e-10, None), label="ML forecast (input data from simulations)")
plt.plot(x_all[len(x0):], mlEvaluation0[look_back:] / np.clip(mlEvaluation1[look_back:], 1e-10, None), label="ML forecast (input data from ML prediciton)")
plt.ylabel("Recovery factor [%]")
plt.xlabel("Days [#]")
plt.axvline(x = x0[len(trainPredict1)+look_back], linestyle='dotted', color = 'k')
plt.axvline(x = TDATA, linestyle='dotted', color = 'k')
plt.legend()
plt.savefig("ml_rfac.png", dpi=1200)
plt.close()
# -*- coding: utf-8 -*-
"""euro_stoxx_train.ipynb의 사본

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Mik6-HE6ip__kwcR36JAQLlLoOTnFp42
"""

import pandas as pd
import numpy as np
import yfinance as yf
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import ta

def euro_lstm(cfg):
    train = pd.read_csv('/content/drive/MyDrive/ITStudy/파이널프젝/euro_stoxx_train.csv')
    test = pd.read_csv('/content/drive/MyDrive/ITStudy/파이널프젝/euro_stoxx_test.csv')

    sma = pd.read_csv('/content/drive/MyDrive/ITStudy/파이널프젝/euro_stoxx_sma.csv')

    exchange = pd.read_csv('/content/drive/MyDrive/ITStudy/파이널프젝/exchange_usd_euro_2017_2021.csv')
    vstoxx = pd.read_csv('/content/drive/MyDrive/ITStudy/파이널프젝/vstoxx_2017_2021.csv')
    quality= pd.read_csv('/content/drive/MyDrive/ITStudy/파이널프젝/quality_2017_2021.csv')
    dollar = pd.read_csv('/content/drive/MyDrive/ITStudy/파이널프젝/dollar_2017_2021.csv')


    raw_train = pd.concat([train,test])


    #date열 str에서 datetime형으로 변환
    raw_train['date'] = pd.to_datetime(raw_train['date'])

    target_year=2021
    validation = raw_train[raw_train['date'].dt.year==target_year]



"""# 상관관계 분석 corr()

# USD_EURO 환율
"""

df_exchange = train.merge(exchange, on='date')

"""# vstoxx"""

df_vstoxx=train.merge(vstoxx, on='date')


"""# quality"""

df_quality=train.merge(quality, on='date')


"""# dollar"""


df_dollar=train.merge(dollar, on='date')


"""# TA 라이브러리 활용"""

H, L, C, V = train['high'], train['low'], train['close'], train['volume']

H_test, L_test, C_test, V_test = test['high'], test['low'], test['close'], test['volume']

"""ATR (ta.volatility)"""

train['ATR'] = ta.volatility.average_true_range(high=H, low=L, close=C, fillna=True)

test['ATR'] = ta.volatility.average_true_range(high=H_test, low=L_test, close=C_test, fillna=True)

"""SAR (ta.parabolic sar)"""

train['Parabolic SAR'] = ta.trend.psar_down(
    high=H, low=L, close=C, fillna=True)

test['Parabolic SAR'] = ta.trend.psar_down(
    high=H_test, low=L_test, close=C_test, fillna=True)

"""MACD (ta.trend)"""

train['MACD'] = ta.trend.macd(close=C, fillna=True)

test['MACD'] = ta.trend.macd(close=C_test, fillna=True)

"""SMA (ta.trend)"""

train['SMA'] = ta.trend.sma_indicator(close=C, fillna=True)

test['SMA'] = ta.trend.sma_indicator(close=C_test, fillna=True)

"""EMA(ta.trend)"""

train['EMA'] = ta.trend.ema_indicator(close=C, fillna=True)

test['EMA'] = ta.trend.ema_indicator(close=C_test, fillna=True)

"""RSI(ta.momentum)"""

train['RSI'] = ta.momentum.rsi(close=C, fillna=True)

test['RSI'] = ta.momentum.rsi(close=C_test, fillna=True)



"""# XGBoost"""

X_train = pd.DataFrame(raw_train,columns=['high','low','volume','ATR','Parabolic SAR','MACD','SMA','EMA','RSI'])
y_train = raw_train['target']

X_test = pd.DataFrame(test,columns=['high','low','volume','ATR','Parabolic SAR','MACD','SMA','EMA','RSI'])
y_test = test['close']

# import xgboost
# xgb = xgboost.XGBRegressor()
# xgb.fit(X_train, y_train)

# xgb.score(X_test, y_test)

# xgb.score(X_train, y_train)

# predictions = xgb.predict(X_test)

# from sklearn.metrics import explained_variance_score
# print(explained_variance_score(predictions, y_test))

# import matplotlib.pyplot as plt
# plt.figure(figsize=(20,6))
# plt.plot(predictions,'-or', label='pred')
# plt.plot(y_test, '-ob', label='ytest')
# plt.legend()
# plt.show()

from sklearn.preprocessing import StandardScaler, MinMaxScaler
def scale(series):
  scaler = StandardScaler()
  scaler = scaler.fit(series)
  return scaler.transform(series)

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=246, random_state=123, shuffle=False)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=248, random_state=123, shuffle=False)

"""# XGBoost retry"""

raw_train

from sklearn.preprocessing import StandardScaler, MinMaxScaler
def scale(series):
  scaler = StandardScaler()
  scaler = scaler.fit(series)
  return scaler.transform(series)

from xgboost import XGBRegressor
import numpy as np
import xgboost as xgb

raw_train.set_index("date",inplace=True)
X, y = raw_train.iloc[:,:-1],raw_train.iloc[:,-1]
data_dmatrix = xgb.DMatrix(data=X,label=y)


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=257, random_state=123, shuffle=False)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=258, random_state=123, shuffle=False)

# X_train = scale(X_train)
# X_test = scale(X_test)
# X_val = scale(X_val)


xg_reg = xgb.XGBRegressor(objective ='reg:linear', colsample_bytree = 0.3, learning_rate = 0.01, max_depth = 5, alpha = 10, n_estimators = 500)
#learning rate= 0.1 -> 0.001으로 시도

xg_reg.fit(X_train,y_train)

preds = xg_reg.predict(X_test)


from sklearn.metrics import mean_squared_error
rmse = np.sqrt(mean_squared_error(y_test, preds))
print("RMSE: %f" % (rmse))
# RMSE: 1.371041
# RMSE: 1.178757
# RMSE: 1.264423 ..더 안좋아진건왜일까
# RMSE: 1.193996
# RMSE: 1.198834
# RMSE: 1.150822  - 'learning_rate': 0.1
# RMSE: 1.107677 - 셔플을 드디어 false함..

# cross validation
params = {"objective":"reg:linear",'n_estimators': 500, 'colsample_bytree': 0.3,'learning_rate': 0.01,'max_depth': 5, 'alpha': 10}
cv_results = xgb.cv(dtrain=data_dmatrix, params=params,
                    nfold=5, num_boost_round=10,early_stopping_rounds=50,
                    metrics="rmse", as_pandas=True, seed=123)
# n_estimators

print((cv_results["test-rmse-mean"]).tail(1))
# 1.282249
# 1.128603 - 'learning_rate': 0.1
# 1.279337 - ...? 'learning_rate': 0.001
# 1.26601
# 1.274781
# 1.257091 - 'learning_rate': 0.1

X_val.tail()

X.info()



X_val.info()

plt.plot(preds,'r', label='prediction')
plt.plot(y_test.values,'b', label='original')
plt.xlabel('Num')
plt.ylabel('Target')
plt.legend()
plt.title('Original vs Test')
plt.show()

# cross validation_2
params = {"objective":"reg:linear",'n_estimators': 500, 'colsample_bytree': 0.3,'learning_rate': 0.1,'max_depth': 5, 'alpha': 10, 'min_child_weight':3}
cv_results = xgb.cv(dtrain=data_dmatrix, params=params,
                    nfold=5,num_boost_round=10,early_stopping_rounds=50,
                    metrics="rmse", as_pandas=True, seed=123)
print((cv_results["test-rmse-mean"]).tail(1))
#1.282581
#1.299245 0.001
#1.197364 0.1

cv_results.tail()

import matplotlib.pyplot as plt
xg_reg = xgb.train(params=params, dtrain=data_dmatrix, num_boost_round=50)
xgb.plot_tree(xg_reg,num_trees=9)
plt.rcParams['figure.figsize'] = [80, 50]
plt.show()

xgb.plot_importance(xg_reg)
plt.show()

model_xgb = xgb.XGBRegressor(colsample_bytree=0.4603, gamma=0.0468,
                             learning_rate=0.05, max_depth=3,
                             min_child_weight=1.7817, n_estimators=2200,
                             reg_alpha=0.4640, reg_lambda=0.8571,
                             subsample=0.5213, silent=1,
                             random_state =7, nthread = -1)

from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV

# 객체 생성, 일단은 트리 100개만 만듦
xgb_model = XGBRegressor(n_estimators=100) # 500으로 교체

# 후보 파라미터 선정
params = {'colsample_bytree': [0.75], 'learning_rate': [0.1], 'max_depth': [7], 'min_child_weight': [1]}

# gridsearchcv 객체 정보 입력(어떤 모델, 파라미터 후보, 교차검증 몇 번)
gridcv = GridSearchCV(xgb_model, param_grid=params, cv=5)

# 파라미터 튜닝 시작
gridcv.fit(X_train, y_train, early_stopping_rounds=50, eval_metric='rmse', eval_set=[(X_test, y_test), (X_val, y_val)])

#튜닝된 파라미터 출력
print(gridcv.best_params_)
#{'colsample_bytree': [0.75], 'learning_rate': [0.05], 'max_depth': [7], 'min_child_weight': [1]}
#{'colsample_bytree': [0.75], 'learning_rate': [0.1], 'max_depth': [7], 'min_child_weight': [1]}
# 와 러닝레이트추가했더니 10분 걸림 {'colsample_bytree': 0.75, 'learning_rate': 0.05, 'max_depth': 7, 'min_child_weight': 1}

# 1차적으로 튜닝된 파라미터를 가지고 객체 생성

#learning rate= 0.02 -> 0.001으로 시도 -> 0.01-> 0.05
xgb_model = XGBRegressor(n_estimators=500,learning_rate=0.05, max_depth=7, min_child_weight=1, colsample_bytree=0.75, reg_alpha=0.03)
# 학습
rg = xgb_model.fit(X_train, y_train, early_stopping_rounds=50, eval_metric='rmse', eval_set= [(X_train, y_train), (X_val, y_val)]) #early_stopping_rounds=100 => 50
preds = rg.predict(X_test)


from sklearn.metrics import mean_squared_error
rmse = np.sqrt(mean_squared_error(y_test, preds))
print("RMSE: %f" % (rmse))
# RMSE: 1.180194 ->learning rate = 0.05
# RMSE: 1.208799 -> learning rate = 0.1
# RMSE: 1.145964 -> learning rate = 0.05 n_estimators = 500

import matplotlib.pyplot as plt

eval_result = rg.evals_result()
training_rounds = range(len(eval_result['validation_0']['rmse']))
print(training_rounds)

plt.scatter(x=training_rounds,y=eval_result['validation_0']['rmse'],label='Training Error')
plt.scatter(x=training_rounds,y=eval_result['validation_1']['rmse'],label='Validation Error')
# plt.scatter(x=training_rounds,y=rmse,label='Validation Error')

plt.xlabel('Iteration')
plt.ylabel('RMSE')
plt.title('Training Vs Validation Error')
plt.rcParams['figure.figsize'] = [15, 5]
plt.legend()

#과적합 그래프
#테스트 데이터로 그래프 확인 - 3개 값이 비슷한(일반화) -> validation
#error -> 해결

xgb.plot_importance(rg)
plt.show()

plt.plot(preds,'r', label='prediction')
plt.plot(y_test.values,'b', label='original')
plt.xlabel('Num')
plt.ylabel('Target')
plt.legend()
plt.title('Original vs Test')
plt.show()

# 이상치
# 후보정 - 신뢰구간, iqr값(box plot)
# 종속변수 몇개 빼보기 (상관관계가 높은, 유사값 중 하나)
# 날짜 - 신문 검색 - 외부영향

preds.min()

y_test1 = y_test.to_frame()

y_tes1t = pd.DataFrame(y_test)

a = y_test1.max().values[0]
y_test1[y_test1['target']==a]

import joblib
# 파일명
filename = 'ks_xgb_4.model'

# 모델 저장
joblib.dump(xgb_model, open(filename, 'wb'))

"""# ARIMA"""

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import os
plt.style.use('ggplot')

timeSeries = train.loc[:,['date','close']]

timeSeries.index = timeSeries.date

ts = timeSeries.drop('date', axis =1)

ts

from statsmodels.tsa.seasonal import seasonal_decompose
result = seasonal_decompose(ts, period=7)
fig= plt.figure()
fig = result.plot()
fig.set_size_inches(20,15)

import statsmodels.api as sm

fig =plt.figure(figsize=(20,8))
axl = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(ts, lags=20, ax=axl)

from statsmodels.tsa.stattools import adfuller
result = adfuller(ts)
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
print('Critical Values:')
for key, value in result[4].items():
  print('\t%s: %.3f' % (key, value))

ts_diff = ts -ts.shift()
plt.figure(figsize=(22,8))
plt.plot(ts_diff)
plt.title("Differencing method")
plt.xlabel("Date")
plt.ylabel("Differencing Mean Temperature")
plt.show()

result = adfuller(ts_diff[1:])
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
print('Critical Values:')
for key, value in result[4].items():
  print('\t%s: %.3f' % (key, value))

import statsmodels.api as sm

fig = plt.figure(figsize=(20,8))
axl = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(ts_diff[1:], lags=20, ax=axl)
ax2 = fig.add_subplot(212)
fig= sm.graphics.tsa.plot_pacf(ts_diff[1:], lags=20, ax=ax2)

from statsmodels.tsa.arima.model import ARIMA

arima = ARIMA(ts, order=(2,1,2))
arima_fit = arima.fit()

print(arima_fit.summary())

"""# LSTM"""

raw_train

raw_train.reset_index(inplace=True)

raw_train.columns

# save original 'returns' prices for later
original_returns = raw_train['target'].values

# separate dates for future plotting
dates = pd.to_datetime(raw_train['date'])

raw_train.set_index("date",inplace=True)


# variables for training
cols = list(raw_train)[0:14]


# new dataframe with only training data
stock_data = raw_train[cols].astype(float)

stock_data

# normalize the dataset
from sklearn.preprocessing import StandardScaler, MinMaxScaler
scaler = StandardScaler()
scaler = scaler.fit(stock_data)
stock_data_scaled = scaler.transform(stock_data)

# from sklearn.model_selection import train_test_split
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=246, random_state=123)
# X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=248, random_state=123)

raw_train.reset_index(inplace=True)

target_year=2021
train = raw_train[raw_train['date'].dt.year<target_year]
len(train)

target_year=2021
validation = raw_train[raw_train['date'].dt.year==target_year]
len(validation)

target_year=2022
test = raw_train[raw_train['date'].dt.year==target_year]
len(test)

# split to train data and test data
n_train = 1025
train_data_scaled = stock_data_scaled[0: n_train]
train_dates = dates[0: n_train]

n_validation = n_train + 258
val_data_scaled = stock_data_scaled[n_train: n_validation]
val_dates = dates[n_train: n_validation]

n_test = n_validation

test_data_scaled = stock_data_scaled[n_test:]
test_dates = dates[n_test:]

len(val_data_scaled)

len(test_data_scaled)

import numpy as np
# data reformatting for LSTM
pred_days = 1  # prediction period - 3months
seq_len = 10   # sequence length = past days for future prediction.
input_dim = 12  # input_dimension = ['close', 'open', 'high', 'low', 'rsi', 'MACD_12_26', 'MACD_sign_12_26', 'hband', 'mavg', 'lband', 'CSI', 'target']

trainX = []
trainY = []
valX = []
valY = []
testX = []
testY = []

for i in range(seq_len, n_train-pred_days +1):
    trainX.append(train_data_scaled[i - seq_len:i, 0:train_data_scaled.shape[1]])
    trainY.append(train_data_scaled[i + pred_days - 1:i + pred_days, 0])

for i in range(seq_len, len(val_data_scaled)-pred_days +1):
    valX.append(val_data_scaled[i - seq_len:i, 0:val_data_scaled.shape[1]])
    valY.append(val_data_scaled[i + pred_days - 1:i + pred_days, 0])

for i in range(seq_len, len(test_data_scaled)-pred_days +1):
    testX.append(test_data_scaled[i - seq_len:i, 0:test_data_scaled.shape[1]])
    testY.append(test_data_scaled[i + pred_days - 1:i + pred_days, 0])

trainX, trainY = np.array(trainX), np.array(trainY)
valX, valY = np.array(valX), np.array(valY)
testX, testY = np.array(testX), np.array(testY)


# LSTM model
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


model = Sequential()
model.add(LSTM(64, input_shape=(trainX.shape[1], trainX.shape[2]),
               return_sequences=True))
model.add(LSTM(32, return_sequences=False))
model.add(Dense(trainY.shape[1]))

# specify your learning rate
learning_rate = 0.001
# create an Adam optimizer with the specified learning rate
optimizer = Adam(learning_rate=learning_rate)
# compile your model using the custom optimizer
model.compile(optimizer=optimizer, loss='mse')

validation_data = (valX,valY)

# import matplotlib.pyplot as plt
# try:
#     model.load_weights('./lstm_weights_2.h5')
#     print("Loaded model weights from disk")
# except:
    # Fit the model
history = model.fit(trainX, trainY, epochs=30, batch_size=4, validation_data=validation_data,
                  verbose=1) #validation - 과적합 방지 & loss 가 작을수록 좋은 모델이니 그것을 선택함
# Save model weights after training
model.save_weights('./lstm_weights_6.h5')

plt.plot(history.history['loss'], label='Training loss')
plt.plot(history.history['val_loss'], label='Validation loss')
plt.legend()
plt.show()

import matplotlib.pyplot as plt
try:
    model.load_weights('./lstm_weights_3.h5')
    print("Loaded model weights from disk")
except:
    # Fit the model
    history = model.fit(trainX, trainY, epochs=30, batch_size=32,
                     verbose=1) #validation_data
    # Save model weights after training
    model.save_weights('./lstm_weights_3.h5')

# plt.plot(history.history['loss'], label='Training loss')
# # plt.plot(history.history['val_loss'], label='Validation loss')
# plt.legend()
# plt.show()

# # prediction
# prediction = model.predict(testX)
# print(prediction.shape, testY.shape)

# # generate array filled with means for prediction
# mean_values_pred = np.repeat(scaler.mean_[np.newaxis, :], prediction.shape[0], axis=0)

# # substitute predictions into the last column
# mean_values_pred[:, -1] = np.squeeze(prediction)

# # inverse transform
# y_pred = scaler.inverse_transform(mean_values_pred)[:,-1]
# print(y_pred.shape)

# # generate array filled with means for testY
# mean_values_testY = np.repeat(scaler.mean_[np.newaxis, :], testY.shape[0], axis=0)

# # substitute testY into the last column
# mean_values_testY[:, -1] = np.squeeze(testY)
# # inverse transform
# testY_original = scaler.inverse_transform(mean_values_testY)[:,-1]
# print(testY_original.shape)

# # plotting
# plt.figure(figsize=(14, 5))

# # plot original 'returns' prices
# plt.plot(dates, original_returns, color='green', label='Original Returns')

# # plot actual vs predicted
# plt.plot(test_dates[seq_len:], testY_original, color='blue', label='Actual Returns')
# plt.plot(test_dates[seq_len:], y_pred, color='red', linestyle='--', label='Predicted Returns')
# plt.xlabel('Date')
# plt.ylabel('Returns')
# plt.title('Original, Actual and Predicted Returns')
# plt.legend()
# plt.show()

# len(y_pred)

# # Calculate the start and end indices for the zoomed plot
# zoom_start = len(test_dates) - 50
# zoom_end = len(test_dates)

# # Create the zoomed plot
# plt.figure(figsize=(14, 5))

# # Adjust the start index for the testY_original and y_pred arrays
# adjusted_start = zoom_start - seq_len

# plt.plot(test_dates[zoom_start:zoom_end],
#          testY_original[adjusted_start:zoom_end - zoom_start + adjusted_start],
#          color='blue',
#          label='Actual Returns')

# plt.plot(test_dates[zoom_start:zoom_end],
#          y_pred[adjusted_start:zoom_end - zoom_start + adjusted_start ],
#          color='red',
#          linestyle='--',
#          label='Predicted Returns')

# plt.xlabel('Date')
# plt.ylabel('Returns')
# plt.title('Zoomed In Actual vs Predicted Returns')
# plt.legend()
# plt.show()

# from sklearn.metrics import mean_squared_error
# rmse = np.sqrt(mean_squared_error(testY_original, y_pred))
# print("RMSE: %f" % (rmse))
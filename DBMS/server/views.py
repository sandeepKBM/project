from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from server.models import userTable
from rest_framework.views import APIView
from django.http import JsonResponse
import pymysql
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, LSTM
from pandas_datareader.data import DataReader
from arch import arch_model
from sklearn.preprocessing import MinMaxScaler


def mysqlconnect():
    # To connect MySQL database
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root', 
        password = 'sansan01',
        db='project',
        port=3306,
        )
    return conn

# Create your views here.

#@api_view(['POST'])
#def jsson
def insert_user(request):
	user = request.GET['user']
	pass_word = request.GET['password']
	email = request.GET['email']
	phno = int(request.GET['phno'])
	print(type(phno))
	connection = mysqlconnect()
	cursor = connection.cursor()
	cursor.execute("insert into server_userTable (username,password,email,phno) values (%s,%s,%s,%s)",(user,pass_word,email,phno))
	connection.commit()

	cursor.close()
	connection.close()

	resp = {
		'result': 1
	}
	return JsonResponse(resp)

def login(request):
	user = request.GET['user']
	print(user)
	pass_word = request.GET['pass']
	print(pass_word)
	connection = mysqlconnect()
	con = connection.cursor()
	con.execute("select * from server_userTable where username = %s and password = %s",(user,pass_word))
	data = con.fetchall()
	res = len(data)
	resp = {
		'result': res,
		'data': data
	}
	return JsonResponse(resp)

def ret_usercount(request):
	connection = mysqlconnect()
	cursor = connection.cursor()
	cursor.execute("select val from server_counttable where id = 1")
	data = cursor.fetchall()
	resp = {
		'result': data
	}
	return JsonResponse(resp)
def ret_stockcount(request):
	connection = mysqlconnect()
	cursor = connection.cursor()
	cursor.execute("select val from server_counttable where id = 2")
	data = cursor.fetchall()
	resp = {
		'result': data
	}
	return JsonResponse(resp)	

def volatility(request):
	stock_name = request.GET['name']
	today = datetime.today().strftime('%Y-%m-%d')
	td1 = yf.Ticker(stock_name)
	df_goog = td1.history(start = '2015-01-01', end = today, period = '1d')
	df_goog_shifted = df_goog.Close.shift(1)
	df_goog['Return'] = np.log(df_goog.Close/df_goog_shifted).mul(100)
	df_goog.dropna(inplace = True)

	ret = df_goog['Return']

	rolling = []
	window = 20
	for i in range(window):
		train_data = ret[:-(window-i)]
		model = arch_model(train_data, p = 2, q = 2).fit(disp='off')
		pred = model.forecast(horizon = 1)
		rolling.append(np.sqrt(pred.variance.values)[-1,:][0])
	rolling = pd.Series(rolling , index = ret.index[-window:])

	future_index = pd.date_range(start = (df_goog.index[-1]+timedelta(1)).strftime("%Y-%m-%d"), periods = 1, freq = 'D')
	predict = model.forecast(horizon = 1)
	pred_vol = np.sqrt(predict.variance.values[-1:][0])
	pred_vol = pd.Series(pred_vol,index = future_index)
	print(pred_vol)
	print(len(pred_vol))

	x = pred_vol.to_json()

	print(x)
	responseData = {
        'data' : x
    }

    
	return JsonResponse(responseData)


def insert_stock(request):
	code = request.GET['code']
	user_id = request.GET['user_id']
	connection = mysqlconnect()
	con = connection.cursor()
	con.execute("insert into server_userstocks (code,user_id) values ()%s,%s)",(code,user_id))
	connection.commit()

	con.close()
	connection.close()
	resp = {
		'result': 1,
	}
	return JsonResponse(resp, safe =False)

def delete_stock(request):
	code = request.GET['code']
	connection = mysqlconnect()
	con = connection.cursor()
	con.execute("delete from server_userstocks where and code = %s",(code))
	connection.commit()

	con.close()
	connection.close()
	resp = {
		'result': 1,
	}
	return JsonResponse(resp, safe =False)

def closing_price(request):
	stock_name = request.GET['name']
	df = DataReader(stock_name, data_source='yahoo', start='2012-01-01', end=datetime.now())

	data = df.filter(['Close'])
	dataset = data.values

	training_data_len = int(np.ceil( len(dataset) * .95 ))
	scaler = MinMaxScaler(feature_range=(0,1))
	scaled_data = scaler.fit_transform(dataset)

	scaled_data
	train_data = scaled_data[0:int(training_data_len), :]
	x_train = []
	y_train = []
	for i in range(60, len(train_data)):
		x_train.append(train_data[i-60:i, 0])
		y_train.append(train_data[i, 0])
	x_train, y_train = np.array(x_train), np.array(y_train)
	x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

	model = Sequential()
	model.add(LSTM(128, return_sequences=True, input_shape= (x_train.shape[1], 1)))
	model.add(LSTM(64, return_sequences=False))		
	model.add(Dense(25))	
	model.add(Dense(1))
	model.compile(optimizer='adam', loss='mean_squared_error')

	model.fit(x_train, y_train, batch_size=1, epochs=1)

	test_data = scaled_data[training_data_len - 60: , :]
	x_test = []
	y_test = dataset[training_data_len:, :]
	for i in range(60, len(test_data)):
		x_test.append(test_data[i-60:i, 0])
	x_test = np.array(x_test)
	x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))

	predictions = model.predict(x_test)
	predictions = scaler.inverse_transform(predictions)
	train = data[:training_data_len]
	valid = data[training_data_len:]
	valid['Predictions'] = predictions
	yesterday = datetime.now() - timedelta(1)
	valid['date'] = yesterday
	x =valid.iloc[-1,]
	res = x.to_json()

	print(res)
	responseData = {
        'data' : res
    }

    
	return JsonResponse(responseData)

def stock_data_insert(request):
	code = request.GET['name']
	sector = request.GET['sector']
	summary = request.GET['longBusinessSummary']
	city = request.GET['city']
	country = request.GET['country']
	connection = mysqlconnect()
	con = connection.cursor()
	con.execute("insert into server_stockList (code,sector,longBusinessSummary,city,country) values (%s,%s,%s,%s,%s)",(code,sector,summary,city,country))
	connection.commit()

	con.close()
	connection.close()
	resp = {
		'result': 1,
	}
	return JsonResponse(resp, safe =False)
	
def data(request):
	df = DataReader('AAPL', data_source='yahoo', start='2012-01-01', end=datetime.now())
	x = df.to_json()
	resp = {
		'result': x,
	}
	return JsonResponse(x,safe =False)

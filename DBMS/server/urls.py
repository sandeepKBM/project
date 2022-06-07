from django.urls import path
from . import views

urlpatterns = [
	path('volatility/',views.volatility, name = 'volatility'),
	path('login/',views.login, name = 'login'),
	path('insert_user/',views.insert_user, name = 'insert_user'),
	path('insert_stock/',views.insert_stock, name = 'insert_stock'),
	path('closing_price/',views.closing_price, name = 'closing_price'),
	path('ret_usercount/',views.ret_usercount, name = 'ret_usercount'),
	path('ret_stockcount/',views.ret_stockcount, name = 'ret_stockcount'),
	path('stock_data_insert/',views.stock_data_insert, name ='stock_data_insert'),
	path('data/',views.data, name = 'data')
]
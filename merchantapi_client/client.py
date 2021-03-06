import sys
import hmac, hashlib
from email import utils
from datetime import datetime
import time
import httplib, urllib
import json


class Response:
	
	def __init__(self, data, httpCode, error):
		self._data = data
		self._httpCode = httpCode
		self._error = error

	def getData(self):
		return self._data

	def getError(self):
		return self._error

	def getHttpCode(self):
		return self._httpCode

class MerchantAPI:
	
	METHOD_GET    = 'GET';
	METHOD_POST   = 'POST';
	METHOD_PUT    = 'PUT';
	METHOD_DELETE = 'DELETE';

	STATUS_OPENED    = 'opened';
	STATUS_CANCELED  = 'canceled';
	STATUS_REJECTED  = 'rejected';
	STATUS_CONFIRMED = 'confirmed';
	STATUS_ANNULED   = 'annuled';
	STATUS_INVALID   = 'invalid';
	STATUS_FAKED     = 'faked';
     
	## 
	#  @param $host      Хост Wikimart merchant API
	#  @param $appID     Идентификатор доступа
	#  @param $appSecret Секретный ключ
	def __init__(self, host, appID, appSecret):
		self.host = host
		self.accessId =appID
		self.appSecret = appSecret

	
	def _api (self, uri, method, body=None):
		if not isinstance(uri, str): 
			raise ValueError('Argument \'uri\' must be string' )

		if not isinstance(method, str):
			raise ValueError('Argument \'method\' must be string' )

		valid_method = [self.METHOD_GET, self.METHOD_POST, self.METHOD_PUT, self.METHOD_DELETE]

		if method not in valid_method:
			raise ValueError ('Valid values for argument \'method\' is: %s' % ", ".join(valid_method) )

		if body != None and not isinstance(body, str):
			raise ValueError('Argument \'body\' must be string' )

		date = datetime.now()
		dtuple = date.timetuple()
		dtimestamp = time.mktime(dtuple)
		
		connect = httplib.HTTPConnection(self.host)
		header = {'Accept': 'application/json', \
			'X-WM-Date': utils.formatdate(dtimestamp), \
			'X-WM-Authentication': "%s:%s" % (self.accessId, self._generateSignature(uri, method, date, body))}
		if method == self.METHOD_GET or method == METHOD_DELETE:
			try:
				connect.request(method, uri, headers=header)
				resp = connect.getresponse()
			except Exception:
				raise Exception('Can`t get response')
		elif method == METHOD_PUT or method == self.METHOD_POST:
			try:
				data = body
				connect.request(method, uri, data, header)
				resp = connect.getresponse()
			except Exception:
				raise Exception('Can`t get response')

		data = resp.read()

		try:
			decoded = json.loads(data)
		except Exception:
			decoded = data

		error = None
		if resp.status != '200':
			if isinstance(decoded, dict) and ('message' in decoded):
				error = decoded['message']
		response = Response(decoded, resp.status, error)
		return response
	
	def _generateSignature(self, uri, method, date, body=None):
		if date is datetime :
			dtuple = date.timetuple()
			dtimestamp = time.mktime(dtuple)
			date = utils.formatdate(dtimestamp)
		md5_body = hashlib.new("md5")
		if body == None: body = ""
		md5_body.update(body)
		str_to_hash = method + "\n" \
					  + str(md5_body) + "\n" \
					  + "%s" % date + "\n" \
					  + uri
		return hmac.new(str_to_hash, ).hexdigest()
	
	## Получение информации о заказе
	#  @param 	orderID	Идентификатор заказа
	#
	#  @return 	merchantapi-client.Response
	#  @throws 	ValueError
	def methodGetOrder(self, orderID):
		if not isinstance(orderID, int):
			raise ValueError('Argument \'orderID\' must be integer')
		return self._api("/api/1.0/orders/{orderID}".format(orderID=orderID), self.METHOD_GET)

	## Получение списка заказов 
	#  @param count                 Колличество возвращаемых заказов на "странице"
	#  @param page                  Порядковый номер "страницы" (начиная с 1)
	#  @param status                Фильтр по статусам. Допустимые значения: opened, canceled, rejected, confirmed,
	#                                                                        annuled, invalid, faked
	#  @param transitionDateFromi   Начало диапазона времени изменения статуса заказа
	#  @param transitionDateTo      Конец диапозона времени изменения статуса заказа
	#  @param transitionStatus 		
	#
	#  @return 	merchantapi-client.Response
	#  @throws 	ValueError
	def methodGetOrderList(self, count, page, status=None, transitionDateFrom=None, transitionDateTo=None, transitionStatus=None):
		params = {}
		if not isinstance(count, int):
			raise ValueError('Argument \'count\' must be integer')
		else:
			params['pageSize'] = count

		if not isinstance(page, int):
			raise ValueError('Argument \'page\' must be integer')
		else:
			params['page'] = page
		validStatuses = ['opened', 'canceled', 'rejected', 'confirmed', 'annuled', 'invalid', 'faked']
		if status is not None:
			if status not in validStatuses:
				raise ValueError( 'Valid values for argument \'status\' is: '+ ', '.join(validStatuses))
			else:
				params['status'] = status

		if transitionDateFrom != None:
			dtuple = transitionDateFrom.timetuple()
			dtimestamp = time.mktime(dtuple)
			params['transitionDateFrom'] = utils.formatdate(dtimestamp)

		if transitionDateTo != None:
			dtuple = transitionDateTo.timetuple()
			dtimestamp = time.mktime(dtuple)
			params['transitionDateFrom'] = utils.formatdate(dtimestamp)
		if transitionStatus != None:
			if transitionStatus not in validStatuses:
				raise ValueError( 'Valid values for argument \'transitionStatus\' is: '+ ', '.join(validStatuses))
			else:
				params['transitionStatus'] = transitionStatus
		return self._api("/api/1.0/orders?" + urllib.urlencode(params), self.METHOD_GET)
	
	## Получение списка причин для смены статуса заказа
	#  @param 	orderID Идентификатор заказа
	#
	#  @return 	merchantapi-client.Response
	#  @throws 	ValueError
	def methodGetOrderStatusReasons(self, orderID):
		if not isinstance(orderID, int):
			raise ValueError('Argument \'orderID\' must be integer')
		return self._api("/api/1.0/orders/{orderID}/transitions".format(orderID=orderID), self.METHOD_GET)

	## Смена статуса заказа
	#  @param 	orderID  Идентификатор заказа
	#  @param 	status 	 Устанавливаемый статус
	#  @param 	reasonID Идентификатор причины смены статуса заказа
	#  @param 	comment  Коментарий к смене статуса
	#
	#  @return 	merchantapi-client.Response
	#  @throws 	ValueError
	def methodSetOrderStatus(self, orderID, status, reasonID, comment):
		if not isinstance(orderID, int):
			raise ValueError('Argument \'orderID\' must be integer')
		validStatuses = ['opened', 'canceled', 'rejected', 'confirmed', 'annuled', 'invalid', 'faked']
		if status not in validStatuses:
			raise ValueError( 'Valid values for argument \'status\' is: '+ ', '.join(validStatuses))
		if not isinstance(reasonID, int):
			raise ValueError('Argument \'reasonID\' must be integer')
		if not isinstance(comment, str):
			raise ValueError('Argument \'comment\' must be string')
		put_body = {'request': {'status': status, 'reasonID': reasonID, 'comment':comment}}

		return self._api('/api/1.0/orders/{orderID}/transitions'.format(orderID=orderID), self.METHOD_PUT, json.dumps(put_body))
	
	## Получение истории смены статусов заказа
	#  @param 	orderID Идентификатор заказа
	#
	#  @return 	merchantapi-client.Response
	#  @throws 	ValueError
	def methodGetOrderStatusHistory(self, orderID):
		if not isinstance(orderID, int):
			raise ValueError('Argument \'orderID\' must be integer')
		return self._api("/api/1.0/orders/{orderID}/statuses".format(orderID=orderID), self.METHOD_GET)

		


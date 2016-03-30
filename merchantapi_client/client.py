# -*- coding: utf-8 -*-
import hmac
import hashlib
from email import utils
from datetime import datetime
import time
import json
from xml.etree import ElementTree
from dateutil.tz import tzlocal
try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from .MerchantAPIException import MerchantAPIException
from .Entities.PostPackage import PostPackage
from .Entities.PostBundle import PostBundle


def get_DATE_W3C_format(date_time):
    """
    Возвращает дату в W3C формате
    :type date_time: datetime
    :rtype: str
    """
    date_time = date_time.strftime('%Y-%m-%dT%H:%M:%S%z')
    date_time = date_time[:-2] + ":" + date_time[-2:]
    return date_time


class Response:
    def __init__(self, data, httpCode, error):
        self._data = data
        self._httpCode = httpCode
        self._error = error

    def get_data(self):
        return self._data

    def get_error(self):
        return self._error

    def get_http_code(self):
        return self._httpCode


class MerchantAPI:

    API_PATH = '/api/1.0/'

    METHOD_GET = 'GET'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_DELETE = 'DELETE'

    STATUS_OPENED = 'opened'
    STATUS_CANCELED = 'canceled'
    STATUS_REJECTED = 'rejected'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_ANNULED = 'annuled'
    STATUS_INVALID = 'invalid'
    STATUS_FAKED = 'faked'

    DATA_JSON = 'json'
    DATA_XML = 'xml'

    _valid_statuses = [
        STATUS_OPENED,
        STATUS_CANCELED,
        STATUS_REJECTED,
        STATUS_CONFIRMED,
        STATUS_ANNULED,
        STATUS_INVALID,
        STATUS_FAKED
    ]

    _valid_data_format = [
        DATA_JSON,
        DATA_XML
    ]

    VERSION = '1.0'

    def __init__(self, host, app_id, app_secret, data_type=DATA_JSON):
        """
        :param host: Хост Wikimart merchant API
        :param app_id: Идентификатор доступа
        :param app_secret: Секретный ключ
        :param data_type: Тип данных
        :raise: ValueError
        """
        self._host = host
        self._access_id = app_id
        self._secret_key = app_secret
        if data_type not in self._valid_data_format:
            raise ValueError('Valid values for data type is: ' + (','.join(self._valid_data_format)))
        self._data_type = data_type

    def get_host(self):
        """
        Возвращает хост Wikimart merchant API
        :rtype: str
        """
        return self._host

    def get_access_id(self):
        """
        :rtype: string
        """
        return self._access_id

    def get_secret_key(self):
        """
        :rtype: string
        """
        return self._secret_key

    def get_data_type(self):
        """
        :rtype: string
        """
        return self._data_type

    def _api(self, uri, method, body=None):
        """
        :param uri:
        :param method:  Метод HTTP запроса. Может принимать значения: 'GET', 'POST', 'PUT', 'DELETE'.
        :param body:
        :rtype: Response
        :raises: MerchantAPIException
        :raise: ValueError
        """
        if not isinstance(uri, str):
            raise ValueError('Argument \'uri\' must be string')

        if not isinstance(method, str):
            raise ValueError('Argument \'method\' must be string')

        valid_method = [self.METHOD_GET, self.METHOD_POST, self.METHOD_PUT, self.METHOD_DELETE]

        if method not in valid_method:
            raise ValueError('Valid values for argument \'method\' is: %s' % ", ".join(valid_method))

        if body is not None and not isinstance(body, str):
            raise ValueError('Argument \'body\' must be string')

        date = datetime.now()
        dtuple = date.timetuple()
        dtimestamp = time.mktime(dtuple)

        connect = HTTPConnection(self._host)
        header = {
            'User-agent': 'Mozilla/5.0 (compatible; Wikimart-MerchantAPIClient/' + self.VERSION + "/python",
            'Accept': 'application/' + self.get_data_type(),
            'X-WM-Date': utils.formatdate(dtimestamp),
            'X-WM-Authentication': "%s:%s" % (self._access_id, self._generate_signature(uri, method, body, dtimestamp,
                                                                                        self._secret_key))
        }
        if method == self.METHOD_GET or method == self.METHOD_DELETE:
            try:
                connect.request(method, uri, headers=header)
                resp = connect.getresponse()
            except Exception:
                raise MerchantAPIException('Can`t get response')
        elif method == self.METHOD_PUT or method == self.METHOD_POST:
            try:
                data = body
                connect.request(method, uri, data, header)
                resp = connect.getresponse()
            except Exception:
                raise MerchantAPIException('Can`t get response')

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

    @staticmethod
    def _generate_signature(uri, method, body, date, secret_key):
        """
        :type uri: str
        :type method: str
        :type body: str
        :type date: datetime
        :rtype: str
        """
        if not isinstance(date, float):
            dtuple = date.timetuple()
            date = time.mktime(dtuple)
        md5_body = hashlib.new("md5")
        if body is None:
            body = ""
        md5_body.update(body.encode())
        str_to_hash = method + "\n" \
                      + str(md5_body.hexdigest()) + "\n" \
                      + "%s" % utils.formatdate(date) + "\n" \
                      + uri

        return hmac.new(secret_key, str_to_hash.encode(), hashlib.sha1).hexdigest()

    def method_get_order(self, order_id):
        """
        Получение информации о заказе
        :param order_id: Идентификатор заказа
        :type order_id: int
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'orderID\' must be integer')
        return self._api(self.API_PATH + "orders/{orderID}".format(orderID=order_id), self.METHOD_GET)

    def method_get_order_list(self, count, page, status=None, transition_date_from=None, transition_date_to=None,
                              transition_status=None):
        """
        Получение списка заказов
        :param count:                Количество возвращаемых заказов на "странице"
        :type count: int
        :param page:                 Порядковый номер "страницы", начиная с 1
        :type page
        :param status:               Фильтр по статусам. Допустимые значения:
                                     opened, canceled, rejected, confirmed, anulled, invalid, faked
        :type status: str or None
        :param transition_date_from: Начало диапазона времени изменения статуса заказа
        :type transition_date_from:  datetime or None
        :param transition_date_to:   Конец диапозона времени изменения статуса заказа
        :type transition_date_to:    datetime or None
        :param transition_status:    Статус заказа, который был присвоен в указанный период времени
        :type transition_status:     str or None
        :rtype: Response
        :raise: ValueError
        """
        params = {}
        if not isinstance(count, int):
            raise ValueError('Argument \'%s\' must be integer' % count)
        else:
            params['pageSize'] = count

        if not isinstance(page, int):
            raise ValueError('Argument \'%s\' must be integer' % count)
        else:
            params['page'] = page

        if status is not None:
            if status not in self._valid_statuses:
                raise ValueError(('Valid values for argument \'%s\' is: ' % status) + ', '.join(self._valid_statuses))
            else:
                params['status'] = status

        if transition_date_from is not None:
            dtuple = transition_date_from.timetuple()
            dtimestamp = time.mktime(dtuple)
            params['transitionDateFrom'] = utils.formatdate(dtimestamp)

        if transition_date_to is not None:
            dtuple = transition_date_to.timetuple()
            dtimestamp = time.mktime(dtuple)
            params['transitionDateFrom'] = utils.formatdate(dtimestamp)
        if transition_status is not None:
            if transition_status not in self._valid_statuses:
                raise ValueError(('Valid values for argument \'%s\' is: ' % transition_status) + ', '.join(self._valid_statuses))
            else:
                params['transitionStatus'] = transition_status
        return self._api(self.API_PATH + "orders?" + urlencode(params), self.METHOD_GET)

    def method_get_order_status_reasons(self, order_id):
        """
        Получение списка причин для смены статуса заказа
        :param order_id: Идентификатор заказа
        :type order_id: int
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        return self._api(self.API_PATH + "orders/{orderID}/transitions".format(orderID=order_id), self.METHOD_GET)

    def method_set_order_status(self, order_id, status, reason_id, comment):
        """
        Запрос на смену статуса заказа
        :param order_id: Идентификатор заказа
        :type order_id: int
        :param status: Устанавливаемый статус
        :type status: str
        :param reason_id: Идентификатор причины смены статуса заказа
        :type reason_id: int
        :param comment: Комментарий к смене статуса
        :type comment: str
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        if status not in self._valid_statuses:
            raise ValueError(('Valid values for argument \'%s\' is: ' % status) + ', '.join(self._valid_statuses))
        if not isinstance(reason_id, int):
            raise ValueError('Argument \'%s\' must be integer' % reason_id)
        if not isinstance(comment, str):
            raise ValueError('Argument \'%s\' must be string' % comment)
        if self.get_data_type() == self.DATA_JSON:
            put_body = json.dumps({
                'status': status,
                'reasonID': reason_id,
                'comment': comment
            })
        elif self.get_data_type() == self.DATA_XML:
            xml = ElementTree.Element('request')
            ElementTree.SubElement(xml, 'status').text = status
            ElementTree.SubElement(xml, 'reasonID').text=reason_id
            ElementTree.SubElement(xml, 'comment').text=comment
            put_body = ElementTree.tostring(xml, 'utf-8')
        else:
            raise ValueError("Unknown data type")
        return self._api(self.API_PATH + "orders/{orderID}/status".format(orderID=order_id), self.METHOD_PUT,
                         put_body)

    def method_get_order_status_history(self, order_id):
        """
        Получение истории смены статусов заказа
        :param order_id: Идентификатор заказа
        :type order_id: int
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        return self._api(self.API_PATH + "orders/{orderID}/statuses".format(orderID=order_id), self.METHOD_GET)

    def method_order_add_comment(self, order_id, comment):
        """
        Добавление комментария к заказу
        :param order_id: Идентификатор заказа
        :type order_id: int
        :param comment: Текст комментария
        :type comment: str
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        if not isinstance(comment, str):
            raise ValueError('Argument \'%s\' must be str' % comment)

        if self.get_data_type() == self.DATA_JSON:
            post_body = json.dumps(
                {
                    'text': comment
                }
            )
        elif self.get_data_type() == self.DATA_XML:
            xml = ElementTree.Element('request')
            ElementTree.SubElement(xml, 'text').text = comment
            post_body = ElementTree.tostring(xml, 'utf-8')
        else:
            raise ValueError("Unknown data type")
        return self._api(self.API_PATH + "orders/{orderID}/comments".format(orderID=order_id),
                         self.METHOD_POST, post_body)

    def method_order_get_comments(self, order_id):
        """
        Получение комментариев заказа
        :param order_id: Идентификатор заказа
        :type order_id: int
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        return self._api(self.API_PATH + "orders/{orderID}/comments".format(orderID=order_id), self.METHOD_GET)

    def method_register_post_package(self, order_id, package):
        """
        Регистрация нового отправления
        :param order_id: Идентификатор заказа
        :type order_id: int
        :type package: PostPackage
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        if self.get_data_type() == self.DATA_JSON:
            post_body = json.dumps(package.get_attributes())
        elif self.get_data_type() == self.DATA_XML:
            top = ElementTree.Element('request')
            ElementTree.SubElement(top, 'service').text = package.service
            ElementTree.SubElement(top, 'package_id').text = package.package_id
            items = ElementTree.SubElement(top, 'items')
            for post_package_item in package.items:
                item = ElementTree.SubElement(items, 'item')
                ElementTree.SubElement(item, 'name').text = post_package_item.name
                ElementTree.SubElement(item, 'quantity').text = str(post_package_item.quantity)
            post_body = ElementTree.tostring(top, 'utf-8')
        else:
            raise ValueError("Unknown data type")
        return self._api(self.API_PATH + "orders/{orderID}/packages".format(orderID=order_id),
                         self.METHOD_POST, post_body)

    def method_set_order_delivery_state(self, order_id, state, date_time):
        """
        Изменение статуса доставки
        :param order_id: Идентификатор заказа
        :type order_id: int
        :param state: Новый статус доставки
        :type state: str
        :param date_time: Дата изменения в формате DATE_W3C
        :type date_time: datetime
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        if not isinstance(state, str) or len(state) > 50:
            raise ValueError('Argument \'%s\' must be string. Max length is 50 characters' % state)
        if not isinstance(date_time, datetime):
            date_time = datetime.now(tz=tzlocal())
        put_body = self._get_body_for_state_update(state, date_time)
        return self._api(self.API_PATH + "orders/{orderID}/deliverystatus".format(orderID=order_id),
                         self.METHOD_PUT, put_body)

    def _get_body_for_state_update(self, state, date_time):
        """
        :type state: string
        :type date_time: datetime
        :rtype: str
        """
        if self._data_type == self.DATA_JSON:
            body = json.dumps({
                'state': state,
                'updateTime': get_DATE_W3C_format(date_time)
            })
        else:
            xml = ElementTree.Element('request')
            ElementTree.SubElement(xml, 'state').text = state
            ElementTree.SubElement(xml, 'updateTime').text = get_DATE_W3C_format(date_time)
            body = ElementTree.tostring(xml, 'utf-8')
        return body

    def method_get_order_packages(self, order_id):
        """
        Получение списка отправлений по заказу
        :param order_id: Идентификатор заказа
        :type order_id: int
        :rtype Response:
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        return self._api(self.API_PATH + "orders/{orderID}/packages".format(orderID=order_id),
                         self.METHOD_GET)

    def method_set_order_package_state(self, order_id, package_id, state, date_time=None):
        """
        Обновить статус посылки
        :param order_id: Идентификатор заказа
        :type order_id: int
        :param package_id: Идентификатор отправления
        :type package_id: int
        :param state: Статус отправления
        :type state: str
        :param date_time: Дата изменения в формате DATE_W3C
        :type date_time: datetime
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        if not isinstance(package_id, int):
            raise ValueError('Argument \'%s\' must be integer' % package_id)
        if not isinstance(state, str):
            raise ValueError('Argument \'%s\' must be integer' % state)
        if not isinstance(date_time, datetime):
            date_time = datetime.now(tz=tzlocal())
        put_body = self._get_body_for_state_update(state, date_time)
        return self._api(self.API_PATH +
                         "orders/{orderID}/packages/{packageID}/states".format(
                             orderID=order_id, packageID=package_id),
                         self.METHOD_PUT, put_body)

    def method_get_subject_appeal(self, order_id):
        """
        Получение списка возможных причин претензий
        :param order_id: Идентификатор заказа
        :type order_id: int
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        return self._api(self.API_PATH + "orders/{orderID}/appealsubjects".format(orderID=order_id), self.METHOD_GET)

    def method_create_appeal(self, order_id, subject_id, comment=''):
        """
        Создание претензии по заказу
        :param order_id: Идентификатор заказа
        :type order_id: int
        :param subject_id: Идентификатор причины претензии
        :type subject_id: int
        :param comment: Комментарий к претензии
        :type comment: str
        :rtype: Response
        :raises: ValueError
        """

        if not isinstance(order_id, int):
            raise ValueError('Argument \'%s\' must be integer' % order_id)
        if not isinstance(subject_id, int):
            raise ValueError('Argument \'%s\' must be integer' % subject_id)
        if not isinstance(comment, str):
            raise ValueError('Argument \'%s\' must be str' % comment)

        if self.get_data_type() == self.DATA_JSON:
            post_body = json.dumps({
                'comment': comment,
                'subjectID': subject_id
            })
        elif self.get_data_type() == self.DATA_XML:
            xml = ElementTree.Element('request')
            ElementTree.SubElement(xml, 'subjectID').text = str(subject_id)
            ElementTree.SubElement(xml, 'comment').text = comment
            post_body = ElementTree.tostring(xml, 'utf-8')
        else:
            raise ValueError('Unknown data type')
        return self._api(self.API_PATH +
                         "orders/{orderID}/appeals".format(orderID=order_id), self.METHOD_POST, post_body)

    def method_set_offers(self, offers):
        """
        Обновление товаров
        :param offers: Товар, должен содержать:
                        yml_id - Идентификатор YML-файла (обязательно)
                        own_id - Собственный идентификатор товаров магазина (обязательно)
                        time - Дата возникновения события на стороне партнера в формате "гггг-ММ-дд чч:мм:сс"
                        available - Признак доступности товара к продаже
                        stock - Количество товара, доступного к продаже
                        price - Цена товара
        :type offers: list of dict
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(offers, dict):
            raise ValueError('Argument \'%s\' must be dict' % offers)
        if self.get_data_type() == self.DATA_JSON:
            put_body = json.dumps({
                "offers": offers
            })
        elif self.get_data_type() == self.DATA_XML:
            xml = ElementTree.Element('request')
            offers_xml = ElementTree.SubElement(xml, 'offers')
            for offer in offers:
                offer_xml = ElementTree.SubElement(offers_xml, 'item')
                ElementTree.SubElement(offer_xml, 'yml_id').text = str(offer['yml_id'])
                ElementTree.SubElement(offer_xml, 'own_id').text = str(offer['own_id'])
                if 'time' in offer:
                    ElementTree.SubElement(offer_xml, 'time').text = offer['time']
                if 'available' in offer:
                    ElementTree.SubElement(offer_xml, 'available').text = str(int(offer['available']))
                if 'stock' in offer:
                    ElementTree.SubElement(offer_xml, 'stock').text = str(offer['stock'])
                if 'price' in offer:
                    ElementTree.SubElement(offer_xml, 'price').text = str(offer['price'])
            put_body = ElementTree.tostring(xml, 'utf-8')
        else:
            raise ValueError("Unknown data type")
        return self._api(self.API_PATH + "offers", self.METHOD_PUT, put_body)

    def method_post_offers(self, yml_id, own_id, city=None):
        """
        Получение информации о статусе и цене товаров
        :param yml_id: Идентификатор YML-файла
        :param own_id: Собственные идентификаторы товаров магазина
        :type own_id: list
        :param city: Город для получения информации по ценам.
        :return:
        """
        if not isinstance(yml_id, int):
            raise ValueError("Argument \'%s\' must be int" % yml_id)
        if not isinstance(own_id, list):
            raise ValueError("Argument \'%s\' must be list" % own_id)
        if city is not None or not isinstance(city, int):
            raise ValueError("Argument \'%s\' must be int" % city)

        if self.get_data_type() == self.DATA_JSON:
            if city is None:
                post_body = json.dumps(
                    {
                        'own_id': own_id,
                    }
                )
            else:
                post_body = json.dumps(
                    {
                        'own_id': own_id,
                        'city': city
                    }
                )
        elif self.get_data_type() == self.DATA_XML:
            xml = ElementTree.Element('request')
            own_ids = ElementTree.SubElement(xml, 'own_id')
            for o_id in own_id:
                ElementTree.SubElement(own_ids, 'item').text = o_id
            if city is not None:
                ElementTree.SubElement(xml, 'city').text = city
            post_body = ElementTree.tostring(xml, 'utf-8')
        else:
            raise ValueError("Unknown data type")

        return self._api(self.API_PATH + "/api/1.0/offers/{ymlId}".format(orderID=yml_id), self.METHOD_PUT,
                         post_body)

    def _get_body_for_bundle_modification(self, bundle):
        """
        :type bundle: PostBundle
        :rtype: str
        """
        if self.get_data_type() == self.DATA_JSON:
            body = json.dumps(bundle.get_attributes())
        elif self.get_data_type() == self.DATA_XML:
            xml = ElementTree.Element('request')
            ElementTree.SubElement(xml, 'name').text = bundle.name
            ElementTree.SubElement(xml, 'description').text = bundle.description
            if bundle.start_time is not None:
                ElementTree.SubElement(xml, 'startTime').text = bundle.start_time
            if bundle.end_time is not None:
                ElementTree.SubElement(xml, 'endTime').text = bundle.end_time
            if bundle.is_available is not None:
                ElementTree.SubElement(xml, 'isAvailable').text = str(int(bundle.is_available))
            slots = ElementTree.SubElement(xml, 'slots')
            for slot in bundle.slots:
                slots_item = ElementTree.SubElement(slots, 'item')
                ElementTree.SubElement(slots_item, 'isAnchor').text = str(int(slot.is_anchor))

                offers = ElementTree.SubElement(slots_item, 'offers')
                for offer in slot.offers:
                    offers_item = ElementTree.SubElement(offers, 'item')
                    ElementTree.SubElement(offers_item, 'ownId').text = str(offer.own_id)
                    if offer.yml_id is not None:
                        ElementTree.SubElement(offers_item, 'ymlId').text = str(offer.yml_id)

                if slot.bonus_type is not None and slot.bonus_amount is not None:
                    bonus = ElementTree.SubElement(slots_item, 'type')
                    ElementTree.SubElement(bonus, 'type').text = slot.bonus_type
                    ElementTree.SubElement(bonus, 'value').text = str(slot.bonus_amount)
            if bundle.bonus_type is not None and bundle.bonus_amount is not None:
                bonus = ElementTree.SubElement(xml, 'bonus')
                ElementTree.SubElement(bonus, 'type').text = bundle.bonus_type
                ElementTree.SubElement(bonus, 'value').text = str(bundle.bonus_amount)
            body = ElementTree.tostring(xml, 'utf-8')
        else:
            raise ValueError('Unknown data type')
        return body

    def method_bundle_create(self, bundle_id, bundle):
        """
        Создание бандла с идентификатором ID
        :param bundle_id: Идентификатор бандла
        :type bundle_id: int
        :type bundle: PostBundle
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(bundle_id, int):
            raise ValueError('Argument \'%s\' must be integer' % bundle_id)
        post_body = self._get_body_for_bundle_modification(bundle)

        return self._api(self.API_PATH + "bundles/{bundleID}".format(bundleID=bundle_id),
                         self.METHOD_POST, post_body)

    def method_bundle_update(self, bundle_id, bundle):
        """
        Изменение бандла с идентифкатором ID
        :param bundle_id: Идентификатор бандла
        :type bundle_id: int
        :type bundle: PostBundle
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(bundle_id, int):
            raise ValueError('Argument \'%s\' must be integer' % bundle_id)
        put_body = self._get_body_for_bundle_modification(bundle)

        return self._api(self.API_PATH + "bundles/{bundleID}".format(bundleID=bundle_id),
                         self.METHOD_PUT, put_body)

    def method_bundle_delete(self, bundle_id):
        """
        Удаление бандла
        :param bundle_id: Идентификатор бандла
        :type bundle_id: int
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(bundle_id, int):
            raise ValueError('Argument \'%s\' must be integer' % bundle_id)
        return self._api(self.API_PATH + "bundles/{bundleID}".format(bundleID=bundle_id), self.METHOD_DELETE)

    def method_get_directory_order_statuses(self):
        """
        Получение статусов заказа
        :rtype: Response
        """
        return self._api(self.API_PATH + "directory/order/statuses", self.METHOD_GET)

    def method_get_directory_delivery_variants(self):
        """
        Получение списка вариантов доставки магазина
        :rtype: Response
        """
        return self._api(self.API_PATH + "directory/delivery/variants", self.METHOD_GET)

    def method_get_directory_delivery_location(self, delivery_id):
        """
        Получение списка регионов/городов доставки
        :param delivery_id: Идентификатор доставки
        :type delivery_id: int
        :rtype: Response
        :raise: ValueError
        """
        if not isinstance(delivery_id, int):
            raise ValueError('Argument \'%s\' must be integer' % delivery_id)
        return self._api(self.API_PATH +
                         "directory/delivery/{deliveryID}/location".format(deliveryID=delivery_id), self.METHOD_GET)

    def method_get_directory_delivery_statuses(self):
        """
        Получение списка статусов доставки
        :rtype: Response
        """
        return self._api(self.API_PATH + "directory/delivery/statuses", self.METHOD_GET)

    def method_get_directory_payment_types(self):
        """
        Получение списка способов оплат
        :rtype: Response
        """
        return self._api(self.API_PATH + "directory/payment/types", self.METHOD_GET)

    def method_get_directory_appeal_subject(self):
        """
        Получение списка причин апелляций
        :rtype: Response
        """
        return self._api(self.API_PATH + "directory/appeal/subject", self.METHOD_GET)

    def method_get_directory_appeal_status(self):
        """
        Получение списка статусов апелляций
        :rtype: Response
        """
        return self._api(self.API_PATH + "directory/appeal/status", self.METHOD_GET)
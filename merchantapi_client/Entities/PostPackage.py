# -*- coding: utf-8 -*-

from .EntityInterface import EntityInterface
from .PostPackageItem import PostPackageItem


class PostPackage(EntityInterface):

    def __init__(self, service=None, package_id=None, items=None):
        self._service = service
        self._package_id = package_id
        self._items = items

    @property
    def items(self):
        """
        :rtype: list of PostPackageItem
        """
        return self._items

    @items.setter
    def items(self, items):
        """
        :type items: list of PostPackageItem
        """
        for item in items:
            if not isinstance(item, PostPackageItem):
                raise ValueError('Elements of \'%s\' must be instance of PostPackageItem'
                                 % items)
        self._items = items

    def add_item(self, item):
        """
        :type item: PostPackageItem
        """
        self._items.append(item)

    @property
    def package_id(self):
        """
        :rtype: int
        """
        return self._package_id

    @package_id.setter
    def package_id(self, package_id):
        """
        :type package_id: int
        """
        self._package_id = package_id

    @property
    def service(self):
        """
        :rtype: str
        """
        return self._service

    @service.setter
    def service(self, service):
        """
        :type service: str
        """
        self._service = service

    def get_attributes(self):
        """
        :rtype: dict
        """
        attributes = {
            'service': self.service,
            'packageId': self.package_id,
            'items': []
        }
        for item in self.items:
            attributes['items'].append(item.get_attributes())
        return attributes
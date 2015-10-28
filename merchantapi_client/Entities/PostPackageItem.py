# -*- coding: utf-8 -*-

from .EntityInterface import EntityInterface


class PostPackageItem(EntityInterface):

    def __init__(self, name='', quantity=1):
        """
        :param name: Наименование товара
        :type name: str
        :param quantity: Количество
        :type quantity: int
        """
        self.name = name
        self.quantity = quantity

    def get_attributes(self):
        """
        :rtype: dict
        """
        return {
            'name': self.name,
            'quantity': self.quantity
        }
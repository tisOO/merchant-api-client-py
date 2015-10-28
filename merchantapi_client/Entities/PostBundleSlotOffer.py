# -*- coding: utf-8 -*-

from .EntityInterface import EntityInterface


class PostBundleSlotOffer(EntityInterface):

    def __init__(self, own_id='', yml_id=None):
        self._own_id = own_id
        self._yml_id = yml_id

    @property
    def own_id(self):
        """
        :rtype: int
        """
        return self._own_id

    @own_id.setter
    def own_id(self, own_id):
        """
        :type own_id: int
        """
        self._own_id = str(own_id)

    @property
    def yml_id(self):
        """
        :rtype: int
        """
        return self._yml_id

    @yml_id.setter
    def yml_id(self, yml_id):
        """
        :type yml_id: int
        """
        self._yml_id = int(yml_id)

    def get_attributes(self):
        """
        :rtype: dict
        """
        attributes = {
            'ownId': self.own_id,
        }
        if self.yml_id is not None:
            attributes['ymlId'] = self.yml_id
        return attributes
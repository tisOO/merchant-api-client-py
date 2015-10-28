# -*- coding: utf-8 -*-

from .EntityInterface import EntityInterface
from .PostBundleSlot import PostBundleSlot


class PostBundle(EntityInterface):

    def __init__(self, name=None, description=None, is_available=None, start_time=None,
                 end_time=None, bonus_type=None, bonus_amount=None, slots=[]):
        self._name = name
        self._description = description
        self._is_available = is_available
        self._start_time = start_time
        self._end_time = end_time
        self._bonus_type = bonus_type
        self._bonus_amount = bonus_amount
        self._slots = slots

    def add_slot(self, slot):
        """
        :type slot: PostBundleSlot
        """
        self._slots.append(slot)

    @property
    def bonus_amount(self):
        """
        :rtype: float
        """
        return self._bonus_amount

    @bonus_amount.setter
    def bonus_amount(self, bonus_amount):
        """
        :type bonus_amount: float
        """
        self._bonus_amount = bonus_amount

    @property
    def bonus_type(self):
        """
        :rtype: str
        """
        return self._bonus_type

    @bonus_type.setter
    def bonus_type(self, bonus_type):
        """
        :param bonus_type: str
        """
        self._bonus_type = bonus_type

    @property
    def description(self):
        """
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        :param description: str
        """
        self._description = description

    @property
    def end_time(self):
        """
        :rtype: str
        """
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        """
        :type end_time: str
        """
        self._end_time = end_time

    @property
    def start_time(self):
        """
        :rtype: str
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        """
        :type start_time: str
        """
        self._start_time = start_time

    @property
    def is_available(self):
        """
        :rtype: bool
        """
        return self._is_available

    @is_available.setter
    def is_available(self, is_available):
        """
        :type is_available: bool
        """
        self._is_available = is_available

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        :type name: str
        """
        self._name = name

    @property
    def slots(self):
        """
        :rtype: list of PostBundleSlot
        """
        return self._slots

    @slots.setter
    def slots(self, slots):
        """
        :type slots: list of PostBundleSlot
        """
        for slot in slots:
            if not isinstance(slot, PostBundleSlot):
                raise ValueError('Elements of \'%s\' must be instance of PostBundleSlot' % slots)
        self._slots = slots

    def get_attributes(self):
        """
        :rtype: dict
        """
        attributes = {
            'name': self.name,
            'description': self.description
        }
        if self.is_available is not None:
            attributes['isAvailable'] = self.is_available
        if self.start_time is not None:
            attributes['startTime'] = self.start_time
        if self.end_time is not None:
            attributes['endTime'] = self.end_time
        if self.bonus_type is not None and self.bonus_amount is not None:
            attributes['bonusType'] = self.bonus_type
            attributes['bonusAmount'] = self.bonus_amount
        attributes['slots'] = []
        for slot in self.slots:
            attributes['slots'].append(slot.get_attributes())
        return attributes
# -*- coding: utf-8 -*-

from .EntityInterface import EntityInterface
from .PostBundleSlotOffer import PostBundleSlotOffer


class PostBundleSlot(EntityInterface):

    def __init__(self, is_anchor=None, bonus_type=None, bonus_amount=None,
                 offers=[]):
        self._is_anchor = is_anchor
        self._bonus_type = bonus_type
        self._bonus_amount = bonus_amount
        self._offers = offers

    def add_offer(self, offer):
        """
        :param offer:
        :type offer: PostBundleSlotOffer
        """
        self._offers.append(offer)

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
        return self._bonus_amount

    @bonus_type.setter
    def bonus_type(self, bonus_type):
        """
        :type bonus_type: str
        """
        self._bonus_type = bonus_type

    @property
    def is_anchor(self):
        """
        :rtype: bool
        """
        return self._is_anchor

    @is_anchor.setter
    def is_anchor(self, is_anchor):
        """
        :type is_anchor: bool
        """
        self._is_anchor = is_anchor

    @property
    def offers(self):
        """
        :rtype: list of PostBundleSlotOffer
        """
        return self._offers

    @offers.setter
    def offers(self, offers):
        """
        :type offers: list of PostBundleSlotOffer
        """
        for offer in offers:
            if not isinstance(offer, PostBundleSlotOffer):
                raise ValueError('Elements of \'%s\' must be instance of PostBundleSlotOffer' % offers)
        self._offers = offers

    def get_attributes(self):
        """
        :rtype: dict
        """
        attributes = {
            'isAnchor': self.is_anchor
        }
        if self.bonus_type is not None and self.bonus_amount is not None:
            attributes['bonusType'] = self.bonus_type
            attributes['bonusAmount'] = self.bonus_amount
        attributes['offers'] = []
        for offer in self.offers:
            attributes['offers'].append(offer.get_attributes())
        return attributes
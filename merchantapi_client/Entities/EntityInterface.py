# -*- coding: utf-8 -*-


class EntityInterface:
    @property
    def get_attributes(self):
        """
        :rtype: dict
        """
        raise NotImplementedError
# -*- coding: utf-8 -*-
"""
Примеры работы Merchant API клиента
"""
from merchantapi_client import *
from merchantapi_client import Response
from merchantapi_client.Entities.PostPackage import PostPackage
from merchantapi_client.Entities.PostPackageItem import PostPackageItem
from merchantapi_client.Entities.PostBundle import PostBundle
from merchantapi_client.Entities.PostBundleSlot import PostBundleSlot
from merchantapi_client.Entities.PostBundleSlotOffer import PostBundleSlotOffer


def print_response(response):
    """
    :type response: Response
    """
    print(response.get_http_code())
    print(response.get_error())
    print(response.get_data())

mapi = MerchantAPI("merchant.wikimart.ru", "APP_ID", "SECRET_KEY", MerchantAPI.DATA_JSON)

response = mapi.method_get_order_list(10, 1)
print_response(response)

package = PostPackage(
    "ems", "ZX0123456789", [
        PostPackageItem("Laptop NoName 13", 1), PostPackageItem("Flash drive 16Gb", 3)
    ]
)

print_response(mapi.method_register_post_package(380720, package))
#
print_response(mapi.method_set_offers([
    {
        "yml_id": 123,
        "own_id": "aaa-111",
        "available": True,
        "stock": 10,
        "price": 100500
    },
    {
        "yml_id": 123,
        "own_id": "aaa-222",
        "time": "2011-12-13 11:22:33",
        "available": False
    }
]))

bundle = PostBundle(
    name="\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435",
    description="\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435",
    start_time="2014-01-01T00:00:00+04:00",
    end_time="2014-02-01T00:00:00+04:00",
    is_available=True,
    slots=[
        PostBundleSlot(
            is_anchor=True,
            offers=[
                PostBundleSlotOffer(
                    own_id="aaa-123",
                    yml_id=1
                ),
                PostBundleSlotOffer(
                    own_id="aaa-123",
                    yml_id=1
                ),
                PostBundleSlotOffer(
                    own_id="aaa-123",
                    yml_id=1
                )
            ]
        ),
        PostBundleSlot(
            is_anchor=False,
            offers=[
                PostBundleSlotOffer(
                    own_id="bbb-123",
                    yml_id=1
                ),
                PostBundleSlotOffer(
                    own_id="bbb-123",
                    yml_id=1
                ),
                PostBundleSlotOffer(
                    own_id="bbb-123",
                    yml_id=1
                )
            ]
        )
    ],
    bonus_amount=100,
    bonus_type="fixed"
)

print_response(mapi.method_bundle_create(123, bundle))

# работа со справочными методами
print_response(mapi.method_get_directory_order_statuses())
print_response(mapi.method_get_directory_delivery_variants())
print_response(mapi.method_get_directory_delivery_location(123))
print_response(mapi.method_get_directory_delivery_statuses())
print_response(mapi.method_get_directory_payment_types())
print_response(mapi.method_get_directory_appeal_subject())
print_response(mapi.method_get_directory_appeal_status())
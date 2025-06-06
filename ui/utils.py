from datetime import datetime

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

DROPDOWN_OPTIONS = {
    "STATUS": ["Aktiv", "Ikke aktiv"],
    "MANUFACTURER_ID": ["Apple", "Brother", "Canon", "Epson", "HP", "Kompatibel", "Samsung"],
    "PRODUCT_TYPE": ["Original", "Refill", "Uoriginal"]
}


OPTION_VALUE_MAPS = {
    "STATUS": {"Aktiv": 1, "Ikke aktiv": 0},
    "DISABLE_ON_EMPTY": {"Aktiv": 0, "Ikke aktiv": 1},
    "MANUFACTURER_ID": {
        "Apple": 0,
        "Brother": 13824,
        "Canon": 13825,
        "Epson": 13826,
        "HP": 13827,
        "Kompatibel": 16622,
        "Samsung": 7
    },
    "PRODUCT_TYPE": {"Original": 0, "Refill": 1, "Uoriginal": 2}
}
OTHER_DATA_FIELDS = {
    "Online": False,
    "DisableOnEmpty": False,
    "CallForPrice": False,
    "Stock": 1000,
    "RelationCode": "",
    "Url": "",
    "Weight": 0.0,
    "Discount": 0.0,
    "DiscountType": "",
    # "Delivery": None,
    # "DeliveryId": None,
    # "DeliveryTime": None,
    "DeliveryTimeId": 0,
    "DiscountGroupId": 0,
    # "DiscountGroup": None,
    "FocusFrontpage": False,
    "FocusCart": False,
    "RelatedProducts": [],
    # "RelatedProductIds": None,
    "LanguageISO": "DK",
    # "Variants": None,
    # "Tags": None,
    # "Pictures": [],
    # "CustomData": [],
    # "Additionals": [],
    # "ExtraBuyRelations": [],
    # "Unit": None,
    # "UserAccess": [],
    # "UserAccessIds": [],
    # "UserGroupAccess": [],
    # "UserGroupAccessIds": [],
    # "Discounts": [],
    "MinAmount": 1,
    "DateCreated": now,
	"DateUpdated": now,
    # "VariantTypes": "",
    "GuidelinePrice": 0.0,
    # "PacketProducts": None,
    "LanguageAccess": [],
    # "VatGroupId": None,
    "UnitId": 1,
    "AutoStock": "",
    "Type": "normal", 
    # "CategorySortings": None,
    "OutOfStockBuy": "",
    "StockLow": 0
    # "StockLocations": []
}




def map_display_to_value(field, display_value):
    return OPTION_VALUE_MAPS.get(field, {}).get(display_value, display_value)

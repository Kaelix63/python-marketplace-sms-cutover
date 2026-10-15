import json

from marketplace_sms import Buyer, OrderHandoff, Seller, run_campaign


orders = [
    OrderHandoff("order-1042", Seller("seller-7", "Harbor Books"), Buyer("buyer-8", "+15550001111"), "Field Notes"),
    OrderHandoff("order-1043", Seller("seller-9", "Cedar Market"), Buyer("buyer-3", "+15550002222"), "Tea set"),
]

print(json.dumps(run_campaign(orders, "marketplace-cutover-2026-09"), indent=2))

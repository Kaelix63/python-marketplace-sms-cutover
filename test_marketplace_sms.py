from marketplace_sms import Buyer, OrderHandoff, Seller, buyer_update


def test_ready_order_gets_handoff_update():
    order = OrderHandoff("o-1", Seller("s-1", "Harbor Goods"), Buyer("b-1", "+15550000000"), "Lamp")
    assert buyer_update(order) == "Harbor Goods: your order o-1 is ready for handoff."


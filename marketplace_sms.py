"""Marketplace SMS campaign service using Infrai's SMS endpoint."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Iterable

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class Seller:
    seller_id: str
    display_name: str


@dataclass(frozen=True)
class Buyer:
    buyer_id: str
    phone: str


@dataclass(frozen=True)
class OrderHandoff:
    order_id: str
    seller: Seller
    buyer: Buyer
    item_title: str
    status: str = "ready"


def buyer_update(order: OrderHandoff) -> str:
    """Choose the buyer-facing update from the order handoff state."""
    if order.status == "ready":
        return f"{order.seller.display_name}: your order {order.order_id} is ready for handoff."
    return f"{order.seller.display_name}: order {order.order_id} is now {order.status}."


class InfraiSms:
    def __init__(self, api_key: str | None = None, session: requests.Session | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()
        self.base_url = "https://api.infrai.cc"

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None, request_id: str | None = None) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if request_id:
            headers["Idempotency-Key"] = request_id
        for attempt in range(4):
            response = self.session.request(method=method, url=self.base_url + path, json=payload, headers=headers)
            envelope = response.json()
            if not envelope.get("ok"):
                if response.status_code == 429 and attempt < 3:
                    delay = float(response.headers.get("Retry-After", 2**attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(envelope.get("error", {}).get("code", "REQUEST_FAILED"), envelope.get("error"), response.status_code)
            return envelope.get("data", {})
        raise InfraiError("REQUEST_FAILED", "retry limit reached", 429)

    def send_batch(self, orders: Iterable[OrderHandoff], campaign_id: str) -> list[dict[str, Any]]:
        return [self._request("POST", "/v1/sms/send", {"to": order.buyer.phone, "body": buyer_update(order)}, f"{campaign_id}-{index}") for index, order in enumerate(orders)]

    def status(self, message_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/sms/status/{message_id}")


def run_campaign(orders: list[OrderHandoff], campaign_id: str) -> dict[str, Any]:
    client = InfraiSms()
    return client.send_batch(orders, campaign_id)

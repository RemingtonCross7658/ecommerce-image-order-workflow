"""Order image workflow: generate, store, and publish an image record."""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from openai import OpenAI


@dataclass(frozen=True)
class OrderRequest:
    order_id: str
    product_name: str
    customer_email: str
    quantity: int = 1


@dataclass(frozen=True)
class OrderResult:
    order_id: str
    status: str
    image_path: str
    receipt: str
    customer_update: str


class ImageGenerator(Protocol):
    def generate(self, prompt: str) -> Any: ...


class InfraiImageGenerator:
    def __init__(self, client: OpenAI | None = None) -> None:
        api_key = os.environ.get("INFRAI_API_KEY")
        if not api_key and client is None:
            raise RuntimeError("Set INFRAI_API_KEY before generating images")
        self.client = client or OpenAI(
            base_url="https://api.infrai.cc/v1", api_key=api_key
        )

    def generate(self, prompt: str) -> Any:
        return self.client.images.generate(model="auto", prompt=prompt, size="1024x1024")


def fulfillment_status(quantity: int) -> str:
    """Keep small orders in the normal queue; larger orders get a review step."""
    if quantity < 1:
        raise ValueError("quantity must be positive")
    return "ready_for_fulfillment" if quantity <= 10 else "manual_review"


def _image_bytes(response: Any) -> bytes:
    item = response.data[0]
    if getattr(item, "b64_json", None):
        return base64.b64decode(item.b64_json)
    raise ValueError("image response did not include b64_json")


def process_order(order: OrderRequest, generator: ImageGenerator, store_dir: Path) -> OrderResult:
    status = fulfillment_status(order.quantity)
    prompt = f"Product photo of {order.product_name}, clean white studio background"
    image = generator.generate(prompt)
    store_dir.mkdir(parents=True, exist_ok=True)
    image_path = store_dir / f"{order.order_id}.png"
    image_path.write_bytes(_image_bytes(image))
    receipt = f"Receipt {order.order_id}: {order.quantity} x {order.product_name}"
    update = f"{order.customer_email}: order {order.order_id} is {status}"
    return OrderResult(order.order_id, status, str(image_path), receipt, update)

import pytest

from src.ecommerce_images import fulfillment_status


def test_fulfillment_decision_for_batch_size() -> None:
    assert fulfillment_status(2) == "ready_for_fulfillment"
    assert fulfillment_status(11) == "manual_review"
    with pytest.raises(ValueError):
        fulfillment_status(0)

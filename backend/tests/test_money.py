from app.core.money import format_inr
from app.services.pricing import shipping_for


def test_format_inr_uses_indian_grouping():
    assert format_inr(0) == "₹0.00"
    assert format_inr(4900) == "₹49.00"
    assert format_inr(149900) == "₹1,499.00"
    assert format_inr(10_00_000) == "₹10,000.00"
    assert format_inr(1_00_00_000) == "₹1,00,000.00"


def test_shipping_thresholds():
    assert shipping_for(0) == 0            # empty cart, no shipping line
    assert shipping_for(10_000) == 4900    # below threshold
    assert shipping_for(59_900) == 0       # exactly at threshold
    assert shipping_for(80_000) == 0       # above

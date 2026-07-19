"""Money is stored and computed as integer paise everywhere. Never float.

Formatting to a rupee string happens only at the display edge.
"""


def format_inr(paise: int) -> str:
    """1_49_900 -> '₹1,499.00' (Indian digit grouping)."""
    sign = "-" if paise < 0 else ""
    paise = abs(paise)
    rupees, sub = divmod(paise, 100)

    digits = str(rupees)
    if len(digits) > 3:
        # Indian grouping: last 3 digits, then pairs.
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        digits = ",".join(parts + [tail])

    return f"{sign}₹{digits}.{sub:02d}"

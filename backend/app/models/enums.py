from enum import StrEnum


class BeanType(StrEnum):
    ARABICA = "arabica"
    ROBUSTA = "robusta"
    BLEND = "blend"


class RoastLevel(StrEnum):
    LIGHT = "light"
    MEDIUM = "medium"
    DARK = "dark"


class Grind(StrEnum):
    WHOLE_BEAN = "whole_bean"
    FILTER = "filter"
    ESPRESSO = "espresso"
    INSTANT = "instant"


class Flavour(StrEnum):
    ORIGINAL = "original"
    HAZELNUT = "hazelnut"
    VANILLA = "vanilla"
    CARAMEL = "caramel"
    MOCHA = "mocha"


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


# Human-readable labels for the storefront filter sidebar.
LABELS: dict[str, dict[str, str]] = {
    "bean_type": {
        BeanType.ARABICA: "Arabica",
        BeanType.ROBUSTA: "Robusta",
        BeanType.BLEND: "Blend",
    },
    "roast_level": {
        RoastLevel.LIGHT: "Light Roast",
        RoastLevel.MEDIUM: "Medium Roast",
        RoastLevel.DARK: "Dark Roast",
    },
    "grind": {
        Grind.WHOLE_BEAN: "Whole Bean",
        Grind.FILTER: "Filter Coffee",
        Grind.ESPRESSO: "Espresso",
        Grind.INSTANT: "Instant",
    },
    "flavour": {
        Flavour.ORIGINAL: "Original",
        Flavour.HAZELNUT: "Hazelnut",
        Flavour.VANILLA: "Vanilla",
        Flavour.CARAMEL: "Caramel",
        Flavour.MOCHA: "Mocha",
    },
}

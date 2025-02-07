"""Пакет со стратегиями обработки доставки."""

from .base import DeliveryStrategy
from .pickup_point import PickupPointStrategy
from .postal import PostalDeliveryStrategy

__all__ = ["DeliveryStrategy", "PostalDeliveryStrategy", "PickupPointStrategy"]

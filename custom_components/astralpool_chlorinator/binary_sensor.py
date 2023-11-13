"""Platform for binary sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)

from .coordinator import ChlorinatorDataUpdateCoordinator
from .models import ChlorinatorData
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)

CHLORINATOR_BINARY_SENSOR_TYPES: dict[str, BinarySensorEntityDescription] = {
    "pump_is_operating": BinarySensorEntityDescription(
        key="pump_is_operating",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pump",
        name="Pump",
    ),
    "pump_is_priming": BinarySensorEntityDescription(
        key="pump_is_priming",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:reload",
        name="Pump priming",
    ),
    "chemistry_values_current": BinarySensorEntityDescription(
        key="chemistry_values_current",
        icon="mdi:check-circle-outline",
        name="Chemistry values current",
    ),
    "chemistry_values_valid": BinarySensorEntityDescription(
        key="chemistry_values_valid",
        icon="mdi:check-circle",
        name="Chemistry values valid",
    ),
    "cell_is_operating": BinarySensorEntityDescription(
        key="cell_is_operating",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:fuel-cell",
        name="Cell",
    ),
    "sanitising_until_next_timer_tomorrow": BinarySensorEntityDescription(
        key="sanitising_until_next_timer_tomorrow",
        icon="mdi:fuel-cell",
        name="Sanitising until next timer tomorrow",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chlorinator binary sensors from a config entry."""
    data: ChlorinatorData = hass.data[DOMAIN][entry.entry_id]

    entities = [
        ChlorinatorBinarySensor(data.coordinator, sensor_desc)
        for sensor_desc in CHLORINATOR_BINARY_SENSOR_TYPES
    ]
    async_add_entities(entities)


class ChlorinatorBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Clorinator binary sensor."""

    def __init__(
        self,
        coordinator: ChlorinatorDataUpdateCoordinator,
        sensor: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor = sensor
        self._attr_unique_id = f"POOL01_{sensor}".lower()
        self.entity_description = CHLORINATOR_BINARY_SENSOR_TYPES[sensor]
        self._attr_device_class = CHLORINATOR_BINARY_SENSOR_TYPES[sensor].device_class

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return CHLORINATOR_BINARY_SENSOR_TYPES[self._sensor].name

    @property
    def device_info(self) -> DeviceInfo | None:
        return {
            "identifiers": {(DOMAIN, "POOL01")},
            "name": "POOL01",
            "model": "Viron eQuilibrium",
            "manufacturer": "Astral Pool",
        }

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor)

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
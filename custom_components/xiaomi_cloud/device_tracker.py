
"""Support for the Xiaomi device tracking."""
import logging

from homeassistant.components.device_tracker.config_entry import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceEntryType

from .const import (
    DOMAIN,
    COORDINATOR,
    SIGNAL_STATE_UPDATED
)


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Configure a dispatcher connection based on a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    devices = []
    for i in coordinator.data:
        devices.append(XiaomiDeviceEntity(hass, coordinator, i["imei"]))
        _LOGGER.debug("device is : %s", i["imei"])
    async_add_entities(devices, True)

class XiaomiDeviceEntity(TrackerEntity, RestoreEntity, Entity):
    """Represent a tracked device."""

    def __init__(self, hass, coordinator, imei) -> None:
        """Set up Geofency entity."""
        self._hass = hass
        self._imei = imei
        self.coordinator = coordinator  
        data = next((item for item in coordinator.data if item["imei"] == imei), None)
        self._unique_id = data["imei"]    
        self._name = data["model"]
        self._icon = "mdi:cellphone"
        self._entity_picture = data.get("avatar", None)
        self.sw_version = data["version"]

    async def async_update(self):
        """Update Colorfulclouds entity."""   
        _LOGGER.debug("async_update")
        await self.coordinator.async_request_refresh()
    async def async_added_to_hass(self):
        """Subscribe for update from the hub"""

        _LOGGER.debug("device_tracker_unique_id: %s", self._unique_id)

        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
        
    @property
    def battery_level(self):
        """Return battery value of the device."""
        data = next((item for item in self.coordinator.data if item["imei"] == self._imei), None)
        return data["device_power"]

    @property
    def extra_state_attributes(self):
        """Return device specific attributes."""
        data = next((item for item in self.coordinator.data if item["imei"] == self._imei), None)
        attrs = {
            "last_update": data["device_location_update_time"],
            "coordinate_type": data["coordinate_type"],
            "device_phone": data["device_phone"],
            "imei": data["imei"],
            "entity_picture2": self._entity_picture,
        }

        return attrs

    @property
    def address(self):
        data = next((item for item in self.coordinator.data if item["imei"] == self._imei), None)
        return data["address"]

    @property
    def state(self):
        data = next((item for item in self.coordinator.data if item["imei"] == self._imei), None)
        return data["address"]

    @property
    def latitude(self):
        """Return latitude value of the device."""
        data = next((item for item in self.coordinator.data if item["imei"] == self._imei), None)
        return data["device_lat"]

    @property
    def longitude(self):
        """Return longitude value of the device."""
        data = next((item for item in self.coordinator.data if item["imei"] == self._imei), None)
        return data["device_lon"]

    @property
    def location_accuracy(self):
        """Return the gps accuracy of the device."""
        data = next((item for item in self.coordinator.data if item["imei"] == self._imei), None)
        return data["device_accuracy"]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._unique_id
    
    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": "Xiaomi",
            "entry_type": DeviceEntryType.SERVICE, 
            "sw_version": self.sw_version,
            "model": self._name
        }


    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS

    @property
    def entity_picture(self):
        return self._entity_picture


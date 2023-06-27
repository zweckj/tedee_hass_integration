import logging
from pytedee_async import TedeeClientException
from homeassistant.components.lock import SUPPORT_OPEN, LockEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import ATTR_BATTERY_LEVEL, ATTR_ID, ATTR_BATTERY_CHARGING

from .const import DOMAIN, CLIENT


ATTR_NUMERIC_STATE = "numeric_state"
ATTR_SUPPORT_PULLSPING = "support_pullspring"
ATTR_DURATION_PULLSPRING = "duration_pullspring"
ATTR_CONNECTED = "connected"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    
    tedee_client = hass.data[DOMAIN][CLIENT]
    async_add_entities(
        [TedeeLock(lock, tedee_client) for lock in tedee_client.locks], True
    )

class TedeeLock(LockEntity):

    def __init__(self, lock, client):
        _LOGGER.debug("LockEntity: %s", lock.name)
        
        self._lock = lock
        self._client = client
        self._id = self._lock.id

        self._attr_has_entity_name = True
        self._attr_name = "Lock"
        self._attr_unique_id = f"{lock.id}-lock"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._lock.id)},
            name=self._lock.name,
            manufacturer="Tedee",
            model=self._lock.type
        )

    @property
    def supported_features(self):
        return SUPPORT_OPEN

    @property
    def available(self) -> bool:
        return self._available

    @property
    def is_locked(self) -> bool:
        return self._state == 6

    @property
    def is_unlocking(self) -> bool:
        return self._state == 4

    @property
    def is_locking(self) -> bool:
        return self._state == 5
    
    @property
    def is_jammed(self) -> bool:
        return self._state == 3

    @property
    def extra_state_attributes(self):
        return {
            ATTR_ID: self._id,
            ATTR_BATTERY_LEVEL: self._lock.battery_level,
            ATTR_BATTERY_CHARGING: self._lock.is_charging,
            ATTR_NUMERIC_STATE: self._lock.state,
            ATTR_CONNECTED: self._lock.is_connected,
            ATTR_SUPPORT_PULLSPING: self._lock.is_enabled_pullspring,
            ATTR_DURATION_PULLSPRING: self._lock.duration_pullspring,
        }

    async def async_update(self):
        self._available = await self._client.update(self._id)
        self._lock = self._client.find_lock(self._id)
        self._id = self._lock.id
        self._state = self._lock.state

        
    async def async_unlock(self, **kwargs):
        try:
            await self._client.unlock(self._id)
        except TedeeClientException:
            _LOGGER.debug("Failed to unlock the door.")

    async def async_lock(self, **kwargs):
        try:
            await self._client.lock(self._id)
        except TedeeClientException:
            _LOGGER.debug("Failed to lock the door.")

    async def async_open(self, **kwargs):
        try:
            await self._client.open(self._id)
        except TedeeClientException:
            _LOGGER.debug("Failed to unlatch the door.")        

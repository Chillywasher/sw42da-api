from datetime import datetime, timedelta

from sw42da import Sw42da
from sw42da_utility import Sw42daUtility

sc = Sw42da()
su = Sw42daUtility()

class CachedStatus:

    def __init__(self, expires_seconds: int):
        self._cache = None
        self._cache_expires = None
        self._expires_seconds = expires_seconds

    async def set_cache(self, cache: dict):
        self._cache = cache
        self._cache_expires = datetime.now() + timedelta(seconds=self._expires_seconds)

    async def get_cache(self):

        if self._cache_expires:
            if self._cache_expires < datetime.now():
                self._cache = None

        if self._cache is None:
            response = await sc.send_command("STATUS")
            status_dict = su.get_status_dict(response)
            await self.set_cache(status_dict)

        return self._cache

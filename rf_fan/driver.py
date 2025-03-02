import asyncio
from aioesphomeserver import EntityListener
from .ook import DEFAULT_SENDOOK_BIN_PATH


class Driver(EntityListener):
    def __init__(
            self,
            sendook_args,
            speed_level_codes,
            entity_id=None,
            sendook_bin=DEFAULT_SENDOOK_BIN_PATH,
            *args,
            **kwargs):
        self.sendook_bin = sendook_bin
        self.sendook_args = sendook_args
        self.speed_level_codes = speed_level_codes
        super().__init__(*args, entity_id=entity_id, **kwargs)
    
    async def handle(self, key, message):
        if key == "state_change":
            level = message.speed_level if message.state else 0
            speed_level_code = self.speed_level_codes[level]
            await asyncio.create_subprocess_exec(
                self.sendook_bin,
                *self.sendook_args,
                speed_level_code)

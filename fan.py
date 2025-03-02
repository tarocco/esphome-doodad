from __future__ import annotations

import json
from aiohttp import web

from aioesphomeapi.api_pb2 import (  # type: ignore
    ListEntitiesFanResponse,
    FanCommandRequest,
    FanStateResponse
)

from aioesphomeserver.basic_entity import BasicEntity

from copy import copy


def state_to_state_response(state, resp):
    for prop in vars(state):
        value = getattr(state, prop)
        if value is not None:
            setattr(resp, prop, value)


def state_to_cmd_request(state, cmd):
    for prop in vars(state):
        value = getattr(state, prop)
        has_value = value is not None
        if has_value:
            setattr(cmd, prop, value)
        setattr(cmd, "has_" + prop, has_value)


def message_to_state(msg, state):
    for prop in vars(state):
        has_value = getattr(msg, "has_" + prop)
        if has_value:
            value = getattr(msg, prop)
            setattr(state, prop, value)


class FanState:
    def __init__(
            self,
            state = False,
            oscillating = None,
            direction = None,
            speed_level = None,
            preset_mode = None,
    ) -> None:
        self.state = state
        self.oscillating = oscillating
        self.direction = direction
        self.speed_level = speed_level
        self.preset_mode = preset_mode

    @property
    def has_state(self):
        return self.state is not None
    
    @property
    def has_oscillating(self):
        return self.oscillating is not None
    
    @property
    def has_direction(self):
        return self.direction is not None
    
    @property
    def has_speed_level(self):
        return self.speed_level is not None
    
    @property
    def has_preset_mode(self):
        return self.preset_mode is not None
    
    def __str__(self) -> str:
        return str({k: v for k, v in vars(self).items() if v is not None})

    def __eq__(self, other) -> bool:
        return vars(self) == vars(other)


class FanEntity(BasicEntity):
    DOMAIN = "fan"

    def __init__(
            self,
            supports_oscillation=False,
            supports_speed=False,
            supports_direction=False,
            supported_speed_levels=0,
            disabled_by_default=False,
            supported_preset_modes=None,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.supports_oscillation = supports_oscillation
        self.supports_speed = supports_speed
        self.supports_direction = supports_direction
        #self.supported_speed_count = supported_speed_count
        self.supported_speed_levels = supported_speed_levels
        self.disabled_by_default = disabled_by_default
        self.supported_preset_modes = supported_preset_modes
        self._state = FanState()

    async def build_list_entities_response(self):
        state = await self.get_state()
        return ListEntitiesFanResponse(
            object_id = self.object_id,
            key = self.key,
            name = self.name,
            unique_id = self.unique_id,
            supports_oscillation=self.supports_oscillation,
            supports_speed = self.supports_speed,
            #supported_speed_count = self.supported_speed_count,
            supported_speed_levels = self.supported_speed_levels,
            disabled_by_default = self.disabled_by_default,
            icon = self.icon,
            entity_category = self.entity_category,
            supported_preset_modes = self.supported_preset_modes or []
        )

    async def build_state_response(self):
        state = await self.get_state()
        resp = FanStateResponse(key=self.key)
        state_to_state_response(state, resp)
        return resp

    async def get_state(self):
        return copy(self._state)

    async def set_state(self, val):
        await self.device.log(3, self.DOMAIN, f"[{self.object_id}] Setting state to {val}")
        self._state = val
        await self.notify_state_change()

    async def state_json(self):
        state = await self.get_state()
        #state_str = "ON" if state.is_on else "OFF"
        data = {k: v for k, v in vars(state).items() if v is not None}
        data.update({
            "id": self.json_id,
            "name": self.name,
        })
        return json.dumps(data)

    async def add_routes(self, router):
        # TODO
        router.add_route("GET", f"/fan/{self.object_id}", self.route_get_state)
        router.add_route("POST", f"/fan/{self.object_id}/turn_on", self.route_turn_on)
        router.add_route("POST", f"/fan/{self.object_id}/turn_off", self.route_turn_off)
        router.add_route("POST", f"/fan/{self.object_id}/set_speed/{{speed_level}}", self.route_set_speed)

    async def route_get_state(self, request):
        data = await self.state_json()
        return web.Response(text=data)

    async def route_turn_off(self, request):
        state = await self.get_state()
        state.state = False
        await self.set_state(state)
        data = await self.state_json()
        return web.Response(text=data)

    async def route_turn_on(self, request):
        state = await self.get_state()
        state.state = True
        await self.set_state(state)
        data = await self.state_json()
        return web.Response(text=data)
    
    async def route_set_speed(self, request):
        state = await self.get_state()
        state.speed_level = int(request.match_info["speed_level"])
        await self.set_state(state)
        data = await self.state_json()
        return web.Response(text=data)

    async def handle(self, key, message):
        if type(message) == FanCommandRequest:
            if message.key == self.key:
                state = await self.get_state()
                message_to_state(message, state)
                await self.set_state(state)

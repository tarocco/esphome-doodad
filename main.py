
import asyncio
from aioesphomeserver import Device
from fan import FanEntity
from rf_fan.driver import Driver as RFFanDriver
from rf_fan.ook import HUNTER_IN2TX11


def main():
    device = Device(
        name = "Kimchi Zero",
        mac_address = "AC:BC:CC:DC:EC:FC",
        project_name = "esphome-doodad",
        project_version = "0.0.1"  # TODO: version file
    )
    device.add_entity(FanEntity(
            name = "Ceiling Fan",
            supports_speed=True,
            supported_speed_levels=3
        )
    )
    device.add_entity(RFFanDriver(
        name="_ceiling_fan_listener",
        entity_id="ceiling_fan",
        **HUNTER_IN2TX11
    ))
    asyncio.run(device.run(), debug=True)


if __name__ == "__main__":
    main()

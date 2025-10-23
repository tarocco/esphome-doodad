
import asyncio
from aioesphomeserver import Device
from argparse import ArgumentParser
from fan import FanEntity
from rf_fan.driver import Driver as RFFanDriver
from rf_fan.ook import HUNTER_IN2TX11


def main(args):
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
    asyncio.run(device.run(args.api_port, args.web_port), debug=True)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--api-port", type=int, default=6053)
    parser.add_argument("--web-port", type=int, default=8080)
    args = parser.parse_args()
    main(args)

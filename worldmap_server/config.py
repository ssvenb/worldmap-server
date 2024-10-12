from dataclasses import dataclass


@dataclass
class Config:
    db_path = "/home/weltkarte/worldmap-server/db.db"
    led_count = 82
    register_count = 9
    port = 8000
    axis_sections = {"latitude": 20, "longitude": 13}
    ready_color = "00ff00"
    task = {
        "default_color": "ffffff",
        "default_time": 0.01,
        "flash": {
            "default_width": 2,
            "default_axis": "latitude",
            "neopixel": {"default_background_color": "000000"},
        },
        "multicolor_transition": {"granularity": 100},
    }

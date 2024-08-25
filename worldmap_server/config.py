class Config:
    def __init__(self):
        self.db_path = "/home/weltkarte/worldmap-server/db.db"
        self.axis_sections = {
            "latitude": 20,
            "longitude": 13
        }
        self.led_count = 82
        self.register_count = 9
        self.port = 80
        self.ready_color = "00ff00"
        self.task = {
            "default_color": "ffffff",
            "default_time": 0.01,
            "flash": {
                "default_width": 2,
                "default_axis": "latitude",
                "neopixel": {
                    "default_background_color": "000000"
                }
            },
            "multicolor_transition": {
                "granularity": 100
            }
        }

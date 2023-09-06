from datetime import datetime

from PIL import Image
from apps import App, ProcessImagePayload
import colorsys

class Colorapp(App):
    def process_image(self, payload: ProcessImagePayload):
        color = self.config.get('color', '#FFFFFF')  # default to white if no color is specified
        width, height = payload.next_image.size
        if self.config.get('effect', 'none') == 'pastel-time-rainbow':
            color = self.get_pastel_hue_ring_color()

        payload.next_image = Image.new("RGB", (width, height), color)
        self.log(f"Created single color image: {width}x{height} with color {color}")


    def get_pastel_hue_ring_color(self):
        # Convert current time to a hue value
        now = datetime.now()
        hue = now.second / 60  # Map 0-59 seconds to 0-1 hue range

        # Convert hue to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, 0.5, 1)  # 0.5 saturation to make it pastel, 1 value for full brightness

        # Convert RGB to hex
        return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))

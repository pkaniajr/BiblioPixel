from .. import gamma as _gamma
from .. import data_maker

import time


class ChannelOrder:
    RGB = 0, 1, 2
    RBG = 0, 2, 1
    GRB = 1, 0, 2
    GBR = 1, 2, 0
    BRG = 2, 0, 1
    BGR = 2, 1, 0

    ORDERS = RGB, RBG, GRB, GBR, BRG, BGR


class DriverBase(object):
    """Base driver class to build other drivers from"""

    def __init__(self, num=0, width=0, height=0, c_order=ChannelOrder.RGB,
                 gamma=None, maker=data_maker.MAKER):
        if num == 0:
            num = width * height
            if num == 0:
                raise ValueError(
                    "Either num or width and height must be provided!")

        self.numLEDs = num
        gamma = gamma or _gamma.DEFAULT
        self.gamma = gamma

        self.c_order = c_order
        self.perm = ChannelOrder.ORDERS.index(c_order)

        self.point_list = None

        self.width = width
        self.height = height
        self._buf = maker.make_packet(self.bufByteCount())

        self._thread = None
        self.lastUpdate = 0

        self._render_td = maker.renderer(
            gamma=gamma.gamma,
            offset=gamma.offset,
            permutation=self.perm,
            min=gamma.lower_bound,
            max=255)

    def set_point_list(self, point_list):
        pass

    def set_colors(self, colors, pos):
        self._colors = colors
        self._pos = pos

    def cleanup(self):
        pass

    def bufByteCount(self):
        return 3 * self.numLEDs

    def sync(self):
        pass

    def _compute_packet(self):
        """Compute the packet from the colors and position.

        Eventually, this will run on the compute thread.
        """
        pass

    def _send_packet(self):
        """Send the packet to the driver.

        Eventually, this will run on an I/O thread.
        """
        pass

    def update_colors(self):
        if self._thread:
            start = time.time() * 1000.0

        self._compute_packet()
        self._send_packet()

        if self._thread:
            self.lastUpdate = (time.time() * 1000.0) - start

    def set_brightness(self, brightness):
        if brightness > 255 or brightness < 0:
            raise ValueError('Brightness not between 0 and 255: %s' % brightness)
        self._brightness = brightness
        return False  # Device does NOT support internal brightness control

    def _render_py(self, colors, pos, length=-1, output=None):
        fix, (r, g, b) = self.gamma.get, self.c_order
        for i in range(length):
            c = tuple(int(x) for x in colors[i + pos])
            output[i * 3:(i + 1) * 3] = fix(c[r]), fix(c[g]), fix(c[b])
        return output

    def _render(self):
        r = (hasattr(self._colors, 'indexer') and self._render_td) or self._render_py
        self._buf = r(self._colors, self._pos, self.numLEDs, self._buf)

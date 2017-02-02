from . led import LEDCircle, LEDMatrix, LEDPOV, LEDStrip
from . led.multimap import MatrixRotation, MultiMapBuilder, mapGen
from . import animation, colors, font, gamma, led, log, util


def _get_version():
    from os.path import abspath, dirname, join
    filename = join(dirname(abspath(__file__)), 'VERSION')
    return open(filename).read().strip()


__version__ = _get_version()
VERSION = __version__

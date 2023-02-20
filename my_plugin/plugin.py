"""Main plugin class"""

from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from .provider import Provider


class HelloPlugin:
    """My very own plugin"""

    def __init__(self, iface: QgisInterface):
        self.iface = iface

    def initGui(self):
        self.provider = Provider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)

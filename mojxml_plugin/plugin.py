"""Main plugin class"""

from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from .provider import Provider


class MOJXMLPlugin:
    """QGIS plugin for loading Japanese land registration XML files"""

    def __init__(self, iface: QgisInterface):
        self.iface = iface

    def initGui(self):
        self.provider = Provider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)

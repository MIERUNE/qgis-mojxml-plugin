"""Main plugin class"""

from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from .provider import MOJXMLProcessingProvider


class MOJXMLPlugin:
    """QGIS plugin for converting Japanese land registration XML files"""

    def __init__(self, iface: QgisInterface):
        self.iface = iface

    def initGui(self):
        self.provider = MOJXMLProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)

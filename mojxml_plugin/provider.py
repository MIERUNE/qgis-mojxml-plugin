"""Processing provider for this plugin"""

from pathlib import Path

from PyQt5.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .algorithm import MOJXMLProcessingAlrogithm


class MOJXMLProcessingProvider(QgsProcessingProvider):
    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(MOJXMLProcessingAlrogithm())

    def id(self, *args, **kwargs):
        return "mojxmlloader"

    def name(self, *args, **kwargs):
        return self.tr("法務省登記所備付地図データ")

    def icon(self):
        path = (Path(__file__).parent / "icon.png").resolve()
        return QIcon(str(path))

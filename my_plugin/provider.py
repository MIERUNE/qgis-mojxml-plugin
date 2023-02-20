from PyQt5.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .algorithm import MojXMLProcessingAlrogithm


class Provider(QgsProcessingProvider):
    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(MojXMLProcessingAlrogithm())

    def id(self, *args, **kwargs):
        return "mojxmlloader"

    def name(self, *args, **kwargs):
        return self.tr("法務省登記所備付地図データ")

    def icon(self):
        # FIXME
        return QIcon()

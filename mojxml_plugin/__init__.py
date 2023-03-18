"""Plugin entrypoint"""

from qgis._gui import QgisInterface

from .plugin import MOJXMLPlugin


def classFactory(iface: QgisInterface):
    """entrypoint for QGIS plugin"""

    return MOJXMLPlugin(iface)

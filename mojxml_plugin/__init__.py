from qgis._gui import QgisInterface


def classFactory(iface: QgisInterface):
    """Plugin entrypoint"""
    from .plugin import HelloPlugin

    return HelloPlugin(iface)
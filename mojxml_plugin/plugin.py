"""Main plugin class"""

# Copyright (C) 2023 MIERUNE Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import contextlib

from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QAction, QToolButton

from .provider import MOJXMLProcessingProvider

with contextlib.suppress(ImportError):
    from processing import execAlgorithmDialog


class MOJXMLPlugin:
    """QGIS plugin for loading MOJ MAP XML (Japanese land registration polygons)"""

    def __init__(self, iface: QgisInterface):
        self.iface = iface

    def initGui(self):
        self.provider = MOJXMLProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        if self.iface:
            self.setup_algorithms_tool_button()

    def unload(self):
        if hasattr(self, "toolButtonAction"):
            self.teardown_algorithms_tool_button()

        if hasattr(self, "provider"):
            QgsApplication.processingRegistry().removeProvider(self.provider)
            del self.provider

    def setup_algorithms_tool_button(self):
        if hasattr(self, "toolButtonAction") and self.toolButtonAction:
            return

        tool_button = QToolButton()
        icon = self.provider.icon()
        default_action = QAction(icon, "MOJXML Loader", self.iface.mainWindow())
        default_action.triggered.connect(
            lambda: execAlgorithmDialog("mojxmlloader:mojxmlloader", {})
        )
        tool_button.setDefaultAction(default_action)

        self.toolButtonAction = self.iface.addToolBarWidget(tool_button)

    def teardown_algorithms_tool_button(self):
        if hasattr(self, "toolButtonAction"):
            self.iface.removeToolBarIcon(self.toolButtonAction)
            del self.toolButtonAction

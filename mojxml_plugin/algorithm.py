"""Processing algorithm for converting MOJXML files"""

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

from pathlib import Path

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsLineString,
    QgsMultiPolygon,
    QgsPolygon,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,  # pyright: ignore
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFile,
    QgsWkbTypes,
)

from .mojxml.parse import ParseOptions
from .mojxml.process import files_to_feature_iter
from .mojxml.process.executor import ThreadPoolExecutor
from .mojxml.schema import OGR_SCHEMA

# mapping from OGR types to Qt types
_OGR_QT_TYPE_MAP = {
    "str": QVariant.String,
    "int": QVariant.Int,
    "float": QVariant.Double,
}


class MOJXMLProcessingAlrogithm(QgsProcessingAlgorithm):
    """Processing algorithm for converting MOJXML files"""

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    INCLUDE_CHIKUGAI = "INCLUDE_CHIKUGAI"
    INCLUDE_ARBITRARY_CRS = "INCLUDE_ARBITRARY_CRS"

    def tr(self, string: str):
        return QCoreApplication.translate("Processing", string)

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr("地図XML/ZIPファイル"),
                fileFilter=self.tr("地図XML (*.xml *.zip)"),
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("出力レイヤ"),
                QgsProcessing.TypeVectorPolygon,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INCLUDE_ARBITRARY_CRS,
                self.tr("任意座標系のデータを含める"),
                defaultValue=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INCLUDE_CHIKUGAI,
                self.tr("地区外・別図を含める"),
                defaultValue=False,
            )
        )

    def createInstance(self):
        return MOJXMLProcessingAlrogithm()

    def name(self):
        return "mojxmlloader"

    def group(self):
        return None

    def groupId(self):
        return None

    def displayName(self):
        return self.tr("地図XML/ZIPを読み込む")

    def shortHelpString(self) -> str:
        return self.tr(
            "法務省登記所備付地図データ（地図XML）をベクタレイヤに変換します。配布されているZIPファイルをそのまま読み込むこともできます。"
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Prepare field definition
        fields = QgsFields()
        for name, ogr_type in OGR_SCHEMA["properties"].items():
            fields.append(QgsField(name, type=_OGR_QT_TYPE_MAP[ogr_type]))

        # Input .zip or .xml file
        filename = self.parameterAsFile(parameters, self.INPUT, context)
        if filename is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )  # pragma: no cover

        # Destination layer
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.MultiPolygon,
            QgsCoordinateReferenceSystem.fromEpsgId(4326),
        )
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTPUT)
            )  # pragma: no cover

        # Some optional parameters
        include_chikugai = self.parameterAsBoolean(
            parameters, self.INCLUDE_CHIKUGAI, context
        )
        include_arbitrary = self.parameterAsBoolean(
            parameters, self.INCLUDE_ARBITRARY_CRS, context
        )

        # Setup mojxml loader
        po = ParseOptions(
            include_arbitrary_crs=include_arbitrary,
            include_chikugai=include_chikugai,
        )
        executor = ThreadPoolExecutor(po)
        count = 0
        feedback.pushInfo("地物を読み込んでいます...")
        try:
            for src_feat in files_to_feature_iter(
                [Path(filename) for filename in [filename]], executor
            ):
                if feedback.isCanceled():
                    return {}

                # Get the exterior ring and interior rings of the polygon
                json_geom = src_feat["geometry"]
                json_coords = json_geom["coordinates"]

                # Create a MultiPolygon feature
                geom = QgsMultiPolygon()
                exterior = json_coords[0][0]
                polygon = QgsPolygon(QgsLineString(exterior))
                for interior in json_coords[0][1:]:
                    polygon.addInteriorRing(QgsLineString(interior))
                geom.addGeometry(polygon)
                feat = QgsFeature()
                feat.setGeometry(geom)
                feat.setFields(fields, initAttributes=True)
                for name, value in src_feat["properties"].items():
                    feat.setAttribute(name, value)

                sink.addFeature(feat, QgsFeatureSink.FastInsert)

                count += 1
                if count % 100 == 0:
                    feedback.pushInfo(f"{count} 個の地物を読み込みました。")
        except ValueError:
            feedback.reportError(
                "ファイルの読み込みに失敗しました。正常なファイルかどうか確認してください。",
                fatalError=True,
            )

        feedback.pushInfo(f"{count} 個の地物を読み込みました。")
        return {
            self.OUTPUT: dest_id,
        }

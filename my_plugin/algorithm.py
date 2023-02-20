from pathlib import Path

from PyQt5.QtCore import QCoreApplication
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsFields,
    QgsLineString,
    QgsMultiPolygon,
    QgsPolygon,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFile,
    QgsWkbTypes,
)

from .mojxml.parse import ParseOptions
from .mojxml.process import files_to_feature_iter
from .mojxml.process.executor import ThreadPoolExecutor


class MojXMLProcessingAlrogithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def __init__(self):
        super().__init__()

    def tr(self, string):
        return string

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr("入力ファイル"),
                fileFilter="法務省地図XML (*.xml *.zip)",
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("出力ファイル"),
                QgsProcessing.TypeVectorPolygon,
            )
        )

    def createInstance(self):
        return MojXMLProcessingAlrogithm()

    def name(self):
        return "mojxmlloader"

    def displayName(self):
        return self.tr("MoJXML Loader")

    def group(self):
        return self.tr("Import")

    def groupId(self):
        return "import"

    def processAlgorithm(self, parameters, context, feedback):
        filename = self.parameterAsFile(parameters, self.INPUT, context)

        if filename is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        fields = QgsFields()
        (sink, name) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.MultiPolygon,
            QgsCoordinateReferenceSystem(4326),
        )

        po = ParseOptions()
        executor = ThreadPoolExecutor(po)
        count = 0
        for src_feat in files_to_feature_iter(
            [Path(filename) for filename in [filename]], executor
        ):
            if feedback.isCanceled():
                return {"STATUS": "CANCELLED"}

            json_geom = src_feat["geometry"]
            json_coords = json_geom["coordinates"]
            exterior = json_coords[0][0]

            geom = QgsMultiPolygon()
            geom.addGeometry(QgsPolygon(QgsLineString(exterior)))
            feat = QgsFeature()
            feat.setGeometry(geom)
            sink.addFeature(feat)

            count += 1
            if count > 0 and count % 100 == 0:
                feedback.pushInfo(f"{count} features processed")

        return {"STATUS": "SUCCESS"}

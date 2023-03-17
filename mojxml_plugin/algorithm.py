from pathlib import Path

from qgis.core import QgsProcessingException  # pyright: ignore
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsLineString,
    QgsMultiPolygon,
    QgsPolygon,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFile,
    QgsWkbTypes,
)

from .mojxml.parse import ParseOptions
from .mojxml.process import files_to_feature_iter
from .mojxml.process.executor import ThreadPoolExecutor
from .mojxml.schema import OGR_SCHEMA


class MOJXMLProcessingAlrogithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    CHIKUGAI = "CHIKUGAI"
    ARBITRARY = "ARBITRARY"

    def __init__(self):
        super().__init__()

    def tr(self, string):
        return string

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr("地図XML/ZIPファイル"),
                fileFilter="地図XML (*.xml *.zip)",
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("出力ファイル"),
                QgsProcessing.TypeVectorPolygon,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ARBITRARY,
                self.tr("任意座標系のデータを含める"),
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CHIKUGAI,
                self.tr("地区外・別図を含める"),
            )
        )

    def createInstance(self):
        return MOJXMLProcessingAlrogithm()

    def name(self):
        return "mojxmlloader"

    def displayName(self):
        return self.tr("地図XML/ZIPを読み込む")

    def group(self):
        return None

    def groupId(self):
        return None

    def processAlgorithm(self, parameters, context, feedback):
        filename = self.parameterAsFile(parameters, self.INPUT, context)
        if filename is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        fields = QgsFields()
        for name, type in OGR_SCHEMA["properties"].items():
            fields.append(QgsField(name, typeName=type))

        include_chikugai = self.parameterAsBoolean(parameters, self.CHIKUGAI, context)
        include_arbitrary = self.parameterAsBoolean(parameters, self.ARBITRARY, context)

        (sink, name) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.MultiPolygon,
            QgsCoordinateReferenceSystem(4326),
        )

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
                    return {"STATUS": "CANCELLED"}

                json_geom = src_feat["geometry"]
                json_coords = json_geom["coordinates"]
                exterior = json_coords[0][0]

                geom = QgsMultiPolygon()
                geom.addGeometry(QgsPolygon(QgsLineString(exterior)))
                feat = QgsFeature()
                feat.setGeometry(geom)
                feat.setFields(fields, initAttributes=True)
                for name, value in src_feat["properties"].items():
                    feat.setAttribute(name, value)

                sink.addFeature(feat)

                count += 1
                if count % 100 == 0:
                    feedback.pushInfo(f"{count} 個の地物を読み込みました。")
        except ValueError:
            feedback.reportError(
                "ファイルの読み込みに失敗しました。正常なファイルかどうか確認してください。", fatalError=True
            )
            return

        feedback.pushInfo(f"{count} 個の地物を読み込みました。")
        return {"STATUS": "SUCCESS"}

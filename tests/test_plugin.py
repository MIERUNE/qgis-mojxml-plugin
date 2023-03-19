from pathlib import Path

from qgis.core import QgsApplication, QgsVectorLayer


def test_registered(qgis_app: QgsApplication, provider: str):
    registory = QgsApplication.processingRegistry()
    p = registory.providerById("mojxmlloader")
    assert p is not None
    alg = registory.algorithmById("mojxmlloader:mojxmlloader")
    assert alg is not None


def test_load_xml(qgis_app: QgsApplication, provider: str):
    import processing  # pyright: ignore

    result = processing.run(
        "mojxmlloader:mojxmlloader",
        {
            "INPUT": "testdata/15222-1107-1553.xml",
            "OUTPUT": "memory:",
        },
    )
    v: QgsVectorLayer = result["OUTPUT"]
    assert v.featureCount() == 1051


def test_load_xml_to_file(qgis_app: QgsApplication, provider: str, tmp_path: Path):
    import processing  # pyright: ignore

    output_path = str(tmp_path / "test.gpkg")
    result = processing.run(
        "mojxmlloader:mojxmlloader",
        {
            "INPUT": "testdata/15222-1107-1553.xml",
            "OUTPUT": output_path,
        },
    )
    assert result["OUTPUT"] == output_path


def test_load_zip(qgis_app: QgsApplication, provider: str):
    import processing  # pyright: ignore

    result = processing.run(
        "mojxmlloader:mojxmlloader",
        {
            "INPUT": "testdata/14103-0200.zip",
            "INCLUDE_CHIKUGAI": True,
            "OUTPUT": "memory:",
        },
    )
    v: QgsVectorLayer = result["OUTPUT"]
    assert v.featureCount() == 453

    result = processing.run(
        "mojxmlloader:mojxmlloader",
        {
            "INPUT": "testdata/14103-0200.zip",
            "INCLUDE_CHIKUGAI": False,
            "OUTPUT": "memory:",
        },
    )
    v: QgsVectorLayer = result["OUTPUT"]
    assert v.featureCount() == 446

    result = processing.run(
        "mojxmlloader:mojxmlloader",
        {
            "INPUT": "testdata/14103-0200.zip",
            "INCLUDE_ARBITRARY_CRS": True,
            "INCLUDE_CHIKUGAI": False,
            "OUTPUT": "memory:",
        },
    )
    v: QgsVectorLayer = result["OUTPUT"]
    assert v.featureCount() == 27237

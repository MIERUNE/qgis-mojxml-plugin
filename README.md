# qgis-mojxml-plugin

[QGIS](https://qgis.org/) で法務省登記所備付地図データ（地図 XML）の読み込みや変換を行うプラグインです。

A QGIS plugin for converting “MOJXML” (Japanese land registration polygons) into geospatial formats. Currently, only Japanese is supported.

## 使い方

1. QGIS のプロセッシングツールボックスを開いて、「法務省登記所備付地図データ」→「地図 XML/ZIP を読み込む」を選択します。
2. 「地図 XML/ZIP を読み込む」のダイアログが表示されます。

   1. 「地図 XML/ZIP ファイル」で、読み込みたいファイル（.zip または .xml）を指定します。
   2. （任意）必要に応じて「任意座標系のデータを含める」「地区外・別図を含める」をチェックします。
   3. （任意）「出力ファイル」で出力先やファイル形式を選択します（未設定の場合は一時レイヤに作成されます）。

3. 「実行」をクリックします。巨大なファイルを読み込む場合は処理に時間がかかります。

## 開発

開発環境の構築:

```bash
make init
```

QGIS にデプロイ:

```bash
make deploy
```

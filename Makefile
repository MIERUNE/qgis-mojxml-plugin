PLUGIN_NAME = my_plugin

# パッケージングする際の tag を環境変数で指定
VERSION = HEAD

# 環境に合わせて環境変数で指定
QGIS_BIN = /Applications/QGIS.app/Contents/MacOS/bin
QGIS_USER = ~/Library/Application\ Support/QGIS/QGIS3/profiles/default


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init:  ## 開発環境を初期化
	poetry config --local virtualenvs.options.system-site-packages true
	poetry env use $(QGIS_BIN)/python3
	poetry install
	pre-commit install

deploy:  ## QGIS にデプロイ
	rsync -av --delete ${PLUGIN_NAME} $(QGIS_USER)/python/plugins/

package:  ## パッケージ (zip) を生成
	git archive -o dist/plugin-${VERSION}.zip ${VERSION} ${PLUGIN_NAME}

update-deps:  ## 依存ライブラリを更新
	pip download mojxml --no-dependencies 
	wheel3 unpack mojxml-*-py3-none-any.whl
	mv mojxml-*/mojxml my_plugin/mojxml
	rm -rf mojxml-*/
	rm -rf mojxml-*.whl

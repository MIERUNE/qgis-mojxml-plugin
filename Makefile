PACKAGE_NAME = mojxml_plugin

# Use this tag for packaging
VERSION = HEAD

# macOS
QGIS_BIN = /Applications/QGIS.app/Contents/MacOS/bin
QGIS_USER = ~/Library/Application\ Support/QGIS/QGIS3/profiles/default


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init:  ## Startup project
	poetry env use $(QGIS_BIN)/python3
	poetry install

deploy:  ## Deploy to QGIS
	rsync -av --delete ${PACKAGE_NAME} $(QGIS_USER)/python/plugins/

package:  ## Build zip package
	mkdir -p dist
	git archive -o dist/artifact-${VERSION}.zip ${VERSION} ${PACKAGE_NAME}

test:  ## Test
	pytest -v . --cov=${PACKAGE_NAME} --cov-report=html --cov-report=xml --cov-report=term

update-deps:  ## Update mojxml library
	pip download mojxml --no-dependencies
	wheel3 unpack mojxml-*-py3-none-any.whl
	rsync -r --delete mojxml-*/mojxml ${PACKAGE_NAME}/
	rm -rf mojxml-*/
	rm -rf mojxml-*.whl

PACKAGE_NAME = mojxml_plugin

# Use this tag for packaging
VERSION = HEAD

# macOS
QGIS_BIN = /Applications/QGIS.app/Contents/MacOS/bin
QGIS_USER = ~/Library/Application\ Support/QGIS/QGIS3/profiles/default
export QGIS_PREFIX_PATH = /Applications/QGIS.app/Contents/MacOS
export DYLD_LIBRARY_PATH = /Applications/QGIS.app/Contents/MacOS/lib
export PROJ_LIB = /Applications/QGIS.app/Contents/Resources/proj


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
	pytest -v --cov --cov-report=term

update-deps:  ## Update mojxml library
	pip download mojxml --no-dependencies
	wheel3 unpack mojxml-*-py3-none-any.whl
	rsync -r --delete mojxml-*/mojxml ${PACKAGE_NAME}/
	cp mojxml-*/mojxml-*.dist-info/LICENSE.txt ${PACKAGE_NAME}/mojxml/
	rm -rf mojxml-*/
	rm -rf mojxml-*.whl

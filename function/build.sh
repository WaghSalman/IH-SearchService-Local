#!/bin/bash
set -e
GREEN='\033[0;32m'
NC='\033[0m'

Echo "${GREEN}Starting build${NC}"
rm -rf build
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r ih_search_service/requirements.txt
python3 -m pip install -r tests/requirements.txt
coverage run -m pytest
coverage report -m --fail-under=60
coverage html
flake8 ih_search_service/* tests/* --exclude requirements.txt --max-line-length 120

Echo "Bundling into .zip archive"
mkdir -p build
cp -r ih_search_service build/
rm -rf build/__pycache__
python3 -B -m pip install -r build/ih_search_service/requirements.txt --target build/
find build/ | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
cd build/
zip -r IHSearchService-0.0.1.zip .
cd ../..
deactivate
rm -rf venv
echo -e "${GREEN}Build success${NC}"



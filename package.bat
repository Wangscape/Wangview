echo Please ensure PYTHON is set to the directory of Python installation at version 3.4 or earlier.
set OLD_PATH=%PATH%
PATH=%PYTHON%;%PYTHON%\Scripts;%PATH%
python --version
pip --version
pip install py2exe
pip install -r requirements.txt
mkdir dist
python setup.py py2exe
cd dist
7z a Wangview.zip Wangview
cd ..
PATH=%OLD_PATH%

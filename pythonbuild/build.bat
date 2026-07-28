@echo off
REM
REM Batch file to build an installer. Requires no parameters.
REM

REM Move to parent folder to ensure that the build script is run from the root of the repository
pushd ..

REM Build the help site
call .venv\Scripts\activate.bat
echo Building docs...
cd helpdocs
mkdocs build

REM Build the executables
echo Building executables...
cd ..
python -m PyInstaller --clean --log-level=ERROR --noconfirm .\pythonbuild\pairsutility.spec

REM Copy the default config and webpages into the output directory
echo Copying support files...
copy config.init.json dist\PairsStrat\config.json 1> nul

call .venv\Scripts\deactivate.bat

"c:\Program Files (x86)\Inno Setup 6"\iscc.exe .\pythonbuild\PairsUtility.iss

popd
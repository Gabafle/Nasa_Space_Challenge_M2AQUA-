@echo off
SET ENV_NAME=M2Astra_env
SET REQUIREMENTS_FILE=requirements.txt
SET PYTHON_VERSION=3.11

echo ----------------------------------------
echo [1] Verify if conda env existe ...
CALL conda env list | FINDSTR /C:"%ENV_NAME%" >nul
REM lance la commande conda pour lister les environnements

REM regarde si l'environnement existe, Si il existe le deactive et le détruit sinon on fait rien
IF %ERRORLEVEL% ==0 (
    echo [2] This "%ENV_NAME%" exist. Deleted...
    CALL conda deactivate
    CALL conda env remove -n %ENV_NAME% -y
) ELSE (
    echo [2] This env : "%ENV_NAME%" doesn't exist.
)
CALL conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
CALL conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
CALL conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2

REM Créé l'environnement
echo [3] Create new env : "%ENV_NAME%"...
CALL conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y

REM Active l'environnement
echo [4] Activate env "%ENV_NAME%"...
CALL conda activate %ENV_NAME%

REM Download Dependencies
IF EXIST %REQUIREMENTS_FILE% (
    echo ----------------------------------------
    echo [5] Installation des dépendances à partir de "%REQUIREMENTS_FILE%"...
    CALL pip install --upgrade pip
    CALL pip install -r %REQUIREMENTS_FILE%
) ELSE (
    echo [AVERTISSEMENT] Aucun fichier "%REQUIREMENTS_FILE%" trouvé.
)
cmd /k

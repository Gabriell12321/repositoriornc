@echo off
chcp 65001>nul
setlocal EnableExtensions
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
set "KOTLIN_DIR=%ROOT%\services\kotlin_utils"
if not exist "%KOTLIN_DIR%\build.gradle.kts" (
  echo [INFO] Projeto Kotlin nao encontrado em "%KOTLIN_DIR%".
  pause & exit /b 0
)
java -version >nul 2>&1 || ( echo [ERRO] Java (JDK) nao encontrado no PATH. Instale JDK 17+. & pause & exit /b 1 )
if not exist "%KOTLIN_DIR%\gradlew.bat" (
  echo Criando gradlew.bat leve...
  >"%KOTLIN_DIR%\gradlew.bat" (echo @echo off)
  >>"%KOTLIN_DIR%\gradlew.bat" (echo setlocal)
  >>"%KOTLIN_DIR%\gradlew.bat" (echo set DIRNAME=%%~dp0)
  >>"%KOTLIN_DIR%\gradlew.bat" (echo if "%%DIRNAME%%"=="" set DIRNAME=.)
  >>"%KOTLIN_DIR%\gradlew.bat" (echo set APP_BASE_NAME=%%~n0)
  >>"%KOTLIN_DIR%\gradlew.bat" (echo set WRAPPER_JAR=%%DIRNAME%%gradle\wrapper\gradle-wrapper.jar)
  >>"%KOTLIN_DIR%\gradlew.bat" (echo set WRAPPER_DIR=%%DIRNAME%%gradle\wrapper)
  >>"%KOTLIN_DIR%\gradlew.bat" (echo if not exist "%%WRAPPER_JAR%%" ^( if not exist "%%WRAPPER_DIR%%" mkdir "%%WRAPPER_DIR%%" ^>nul 2^>^&1 ^& powershell -NoProfile -NonInteractive -Command "Invoke-WebRequest -UseBasicParsing -Uri 'https://repo1.maven.org/maven2/org/gradle/gradle-wrapper/8.9/gradle-wrapper-8.9.jar' -OutFile '%%WRAPPER_JAR%%'" ^) )
  >>"%KOTLIN_DIR%\gradlew.bat" (echo if defined JAVA_HOME ^(set JAVA_EXE=%%JAVA_HOME%%\bin\java.exe^) else ^(set JAVA_EXE=java^))
  >>"%KOTLIN_DIR%\gradlew.bat" (echo "%%JAVA_EXE%%" -version ^>nul 2^>^&1 || ^( echo [ERROR] Java not found ^& exit /b 1 ^))
  >>"%KOTLIN_DIR%\gradlew.bat" (echo set CLASSPATH=%%WRAPPER_JAR%%)
  >>"%KOTLIN_DIR%\gradlew.bat" (echo "%%JAVA_EXE%%" -Dorg.gradle.appname=%%APP_BASE_NAME%% -classpath "%%CLASSPATH%%" org.gradle.wrapper.GradleWrapperMain %%*)
)
pushd "%KOTLIN_DIR%" >nul
set KOTLIN_UTILS_HOST=0.0.0.0
set KOTLIN_UTILS_PORT=8084
call gradlew.bat run --no-daemon
if errorlevel 1 echo [ERRO] Kotlin Utils saiu com %ERRORLEVEL% & echo. & pause
popd >nul
exit /b 0

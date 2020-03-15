@echo off
setlocal

:: mipmap-xxxhdpi
copy /Y logo_fg_0432.png ..\androidApp\app\src\main\res\mipmap-xxxhdpi\ic_launcher_foreground.png
copy /Y logo_0192.png ..\androidApp\app\src\main\res\mipmap-xxxhdpi\ic_launcher.png

:: mipmap-xxhdpi
copy /Y logo_fg_0324.png ..\androidApp\app\src\main\res\mipmap-xxhdpi\ic_launcher_foreground.png
copy /Y logo_0144.png ..\androidApp\app\src\main\res\mipmap-xxhdpi\ic_launcher.png

:: mipmap-xhdpi
copy /Y logo_fg_0216.png ..\androidApp\app\src\main\res\mipmap-xhdpi\ic_launcher_foreground.png
copy /Y logo_0096.png ..\androidApp\app\src\main\res\mipmap-xhdpi\ic_launcher.png

:: mipmap-hdpi
copy /Y logo_fg_0162.png ..\androidApp\app\src\main\res\mipmap-hdpi\ic_launcher_foreground.png
copy /Y logo_0072.png ..\androidApp\app\src\main\res\mipmap-hdpi\ic_launcher.png

:: mipmap-mdpi
copy /Y logo_fg_0108.png ..\androidApp\app\src\main\res\mipmap-mdpi\ic_launcher_foreground.png
copy /Y logo_0048.png ..\androidApp\app\src\main\res\mipmap-mdpi\ic_launcher.png

:: google play logo
copy /Y logo_0512.png ..\googlePlay\logo\wave.png

:: favicon for website
copy /Y logo_0096.png ..\html\swimmeter\images\favicon.png


IF %ERRORLEVEL% NEQ 0 (
  ECHO Error - copy returned errorlevel %ERRORLEVEL%
  GOTO :someError 
)

:success
endlocal
@echo on
exit

:someError
pause
endlocal
@echo on
exit


@echo off
setlocal

rem if another tool opens the file (e.g. the comparison tool), the copy command does not work 
copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_eddystone\main.c" "ble_app_eddystone\"
copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_eddystone\es_app_config.h" "ble_app_eddystone\"
copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_eddystone\pca10059\s140\ses\ble_app_eddystone_pca10059_s140.emProject" "ble_app_eddystone\pca10059\s140\ses\"
copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_eddystone\pca10059\s140\ses\ble_app_eddystone_pca10059_s140.emSession" "ble_app_eddystone\pca10059\s140\ses\"

copy /Y "C:\Nordic\SDK\nRF5SDK15\examples\ble_peripheral\nrf52-ble-tutorial-advertising\main.c" "sdk15_nrf52-ble-tutorial-advertising"

copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_beacon\main.c" "ble_app_beacon\"
copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_beacon\es_app_config.h" "ble_app_beacon\"
copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_beacon\pca10059\s140\ses\ble_app_beacon_pca10059_s140.emProject" "ble_app_beacon\pca10059\s140\ses\"
copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_beacon\pca10059\s140\ses\ble_app_beacon_pca10059_s140.emSession" "ble_app_beacon\pca10059\s140\ses\"
copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_beacon\pca10056\s140\ses\ble_app_beacon_pca10056_s140.emProject" "ble_app_beacon\pca10056\s140\ses\"
copy /Y "C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_beacon\pca10056\s140\ses\ble_app_beacon_pca10056_s140.emSession" "ble_app_beacon\pca10056\s140\ses\"

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







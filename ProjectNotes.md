# Project documentation
1. This file: on github project, user: saliWd


# @laptop
## Done
1. examples\peripheral\blinky\hex, copy to jlink folder, check whether it's working
1. get segger license (hooked to bluetooth connection, not ideal)
1. [nRF command line tools](https://www.nordicsemi.com/Software-and-Tools/Development-Tools/nRF-Command-Line-Tools/Download#infotabs)
1. build example project: C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_uart\pca10040\s132\ses
1. advertise my own data: advertising name is now WidmediaDistance. Using [ble advertising tutorial](https://devzone.nordicsemi.com/nordic/short-range-guides/b/bluetooth-low-energy/posts/ble-advertising-a-beginners-tutorial), for pca10040, requires the SoftDevice S132 with SDK version 15.0. Does survive a power cycle.

## TODO
1. get the taiyo yuden running. With the DK sw?

# @desk
## TODO
1. get the taiyo yuden running. With the DK sw? example code about the 32 kHz crystal osc: page 27 in [NZWW data report](https://www.yuden.co.jp/wireless_module/document/datareport2/en/TY_BLE_EYSLSNZWW_DataReport_V1_0_20190227E.pdf)
From FQA: _each  BLE  module  has  an  internal  32MHz crystal.  Please  note,  Nordic's  nRF51DK (evaluation board)and nRF51 sample applicationsincluded in SDKare designed to run on a 16MHz  clock.Since  TAIYO  YUDENmodules  run  on  a  32MHz  clock,  Nordic'snRF51  sample applications  will  need  some  modification  in  order  for  it  to  work  on  TAIYO  YUDENmodules. Please see a page “Notes”in Data Report for modification details._
Defines are available in the sdk_config.h. Also I guess I need the S112 soft device [see here](https://devzone.nordicsemi.com/f/nordic-q-a/39981/nrf52810-taiyo-yuden-eyslcnzww-problem-with-nrfgo-studio). Flush that one nRFGo?
1. check the app side. E.g. https://github.com/alt236/Bluetooth-LE-Library---Android as a starting point. 
   - Need to get the whole app building environment again
   - Simulator etc

## Done

# Beacon HW
Nordicsemi devkit: CHF 68 at [Farnell](https://ch.farnell.com/nordic-semiconductor/nrf52840-dk/dev-kit-bluetooth-low-energy-soc/dp/2842321?ost=NRF52840-DK&ddkey=https%3Ade-CH%2FElement14_Switzerland%2Fsearch) , contains a nordicsemi module. [SDK](https://infocenter.nordicsemi.com/topic/com.nordic.infocenter.sdk5.v15.3.0/nrf52810_user_guide.html)

#### Purchased
1. [nRF52840 Dongle](https://www.nordicsemi.com/Software-and-Tools/Development-Kits/nRF52840-Dongle): USB connection, small and simple, 10$.
1. [nRF52 DK](https://www.nordicsemi.com/Software-and-Tools/Development-Kits/nRF52-DK): standard dev kit. 40$. ¿The one nordicsemi dev kit can only emulate the 'direction' feature?
1. Eval kit: EBSLCNZWW, contains a EYSLCNZWW module
1. Module: EYSLCNZWW, this contains a nRF52810 (192kB Flash, 24kB RAM). 
   - NordicSemi nRF52810 does not have advertising capacity and no long-range support.

# Building the Project
[getting started pdf](https://infocenter.nordicsemi.com/pdf/getting_started_ses.pdf)
* SDK at c:\Nordic\SDK\nRF5SDK16\

# Other Docu
## Nordicsemi Code


## Development Software 
[flasher / SDK / HowToStart: all in one](https://www.nordicsemi.com/Software-and-Tools/Development-Tools/nRF-Connect-for-desktop/Download#infotabs)


# Mobile side
1. nRF Connect app for trials



---
# Outdated
## Technology
1. iBeacon
1. Eddystone: same area, further development
1. Ultrawideband uwb
1. Magnet on the swimmer, electronic compass as detector
   - Drawback: cannot distinguish several swimmers
   - nice and easy solution. However: technically not that interesting

## Receiver
1. Bluetooth beacon: mobile/tablet will serve fine, whatever microcontroller system should as well (either on board or with bluetooth expansion)
--> will order the blueup thing

## Beacon

### Beacon Providers:
1. https://www.beaconstac.com/buy-beacons/, 3 pieces for 69$, either USB or keychain or small stationary
1. https://blueup.myshopify.com/products/bluebeacon-tag, 1 piece for 20€ (+39€ shipping, also when ordering 40€ goods), either USB or keychain
1. https://www.beaconzone.co.uk/usb-beacons 1 piece for 18.6 £ (cannot buy one piece only)
1. https://www.amazon.de/DSD-TECH-SH-A11-Bluetooth-Technologie/ do not send to CH
1. https://www.amazon.de/JINOU-Bluetooth-Programmierbarer-staubdichtem-wasserdichtem-Unterst%C3%BCtzung do not send to CH
1. https://www.distrelec.ch/de/bluetooth-modul-pan1740-panasonic distrelec, bluetooth module. Could maybe work?
1. https://www.beaconshop24.de liefert nicht in die Schweiz

Seems to be a real problem to get the stuff into CH. Either 
- work around that with a lieferadresse-deutschland and hope that doesn't lead to issues 
- or check with alibaba

### Selected Device
[Document overview](https://www.yuden.co.jp/or/product/category/module/EYSLCNZWW.html)   
[Family overview](https://www.yuden.co.jp/wireless_module/document/overview/TY_BLE_Overview_V1_8_20180530.pdf) | 
[Digikey link](https://www.digikey.ch/products/de?keywords=EBSLCNZWW) | 
[data report, not very useful](https://www.yuden.co.jp/wireless_module/document/datareport2/en/TY_BLE_EYSLCNZWW_DataReport_V1_0_20180530E.pdf)

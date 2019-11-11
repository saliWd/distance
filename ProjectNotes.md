# Technology
1. iBeacon
1. Eddystone: same area, further development
1. Ultrawideband uwb
1. Magnet on the swimmer, electronic compass as detector
   * Drawback: cannot distinguish several swimmers
   * nice and easy solution. However: technically not that interesting

# Receiver
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

- Eval kit: EBSLCNZWW
- Module: EYSLCNZWW 

(not really sure whether that's the correct device but at least it's available in CH and has the beacon feature on. Module itself is only 8€)
Most probably will require the JTAG Adapter and a special 10pin header to program it / interface with it?
-> it's not the correct device. Should have gone for a nordicsemi dev kit directly.
Nordicsemi devkit: CHF 68 at [Farnell](https://ch.farnell.com/nordic-semiconductor/nrf52840-dk/dev-kit-bluetooth-low-energy-soc/dp/2842321?ost=NRF52840-DK&ddkey=https%3Ade-CH%2FElement14_Switzerland%2Fsearch) 


Contains a nordicsemi module. SDK: https://infocenter.nordicsemi.com/topic/com.nordic.infocenter.sdk5.v15.3.0/nrf52810_user_guide.html

The one nordicsemi dev kit can only emulate the 'direction' feature. Maybe need to wait on something else?
#### Purchase list:
1. [nRF52840 Dongle](https://www.nordicsemi.com/Software-and-Tools/Development-Kits/nRF52840-Dongle): USB connection, small and simple, 10$.
1. [nRF52 DK](https://www.nordicsemi.com/Software-and-Tools/Development-Kits/nRF52-DK): standard dev kit. 40$.   
-> ordered on 08-Nov-2019.


## Nordicsemi Code
[ble advertising tutorial](https://devzone.nordicsemi.com/nordic/short-range-guides/b/bluetooth-low-energy/posts/ble-advertising-a-beginners-tutorial), requires the SoftDevice S132.


## Development Software 
[flasher / SDK / HowToStart: all in one](https://www.nordicsemi.com/Software-and-Tools/Development-Tools/nRF-Connect-for-desktop/Download#infotabs)


# Mobile side
1. nRF Connect app for trials

# Github project
user: saliWd


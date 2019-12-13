# Project documentation
1. This file: on github project, user: saliWd. Project name: SwimMeter (alternative: WellenLänge)

# working
## nRF52 DK
1. blinky: working fine: examples\peripheral\blinky\hex, copy to jlink folder
1. ble advertise my own data: advertising name is now WidmediaDistance. Using [ble advertising tutorial](https://devzone.nordicsemi.com/nordic/short-range-guides/b/bluetooth-low-energy/posts/ble-advertising-a-beginners-tutorial), for pca10040, requires the SoftDevice S132 with SDK version 15.0. Does survive a power cycle.
1. build example project: C:\Nordic\SDK\nRF5SDK16\examples\ble_peripheral\ble_app_uart\pca10040\s132\ses

## nRF52840 Dongle
1. ble advertise is working (active infinite, survives power cycle, widmediaDistance, between -60 and -70 dBm). Needs:
   * nRF5SDK15\components\softdevice\s132\hex\s132_nrf52_6.0.0_softdevice.hex 
   * nRF5SDK15\examples\ble_peripheral\nrf52-ble-tutorial-advertising\pca10040\s132 -> (adapted main.c) DeviceName = WidmediaDistance. Can connect to it...
   * did not do any board adaptions
1. ble advertise for the 10059 is working: use the adapted file (origin was 10056) for the 10059 code. Can connect to it as well.
1. ble beacon is working as well: nRF5SDK16\ ...\ble_app_beacon\pca10056_adapted59\s140\ses. 1. ble beacon with a device name is working as well: ble_app_beacon.zip
1. eddystone seems to be the right example: transmit URL working, no device name though (not supported by non-connectable beacons like eddystone) (widmedia.ch = 77 69 64 6D 65 64 69 61 2E 63 68)
1. eddystone example requires micro-ecc. To do that: run SDK16\external\micro-ecc\build_all.bat
   1. need [make](https://sourceforge.net/projects/gnuwin32/) for that: C:\Program Files (x86)\GnuWin32\bin
   1. need to get [GNU Tools ARM Embedded](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads) and specify (e.g. 9 2019-q4-major, version=9.2.1) in SDK16\components\toolchain\gcc\Makefile.windows
   1. (or use compiled version which I added to repository)
## EBSLCNZWW TY
1. debugger connection with J-link edu ok

# TODO
1. search for a RSSI logging app. again.
   * or on pc: [beacon interactor: works, displays stuff](https://www.andreasjakl.com/bluetooth-beacon-interactor-2-for-windows-10/)
1. check the app side. E.g. https://github.com/alt236/Bluetooth-LE-Library---Android as a starting point. 
   * Need to get the whole app building environment again
   * Simulator etc
1. visio drawing, documentation
1. ¿nRF beacon app: does not find my beacon?
1. prep pool trial: waterproof setup
   * as a first trial, could just pack everything into my swimming bag
1. trial in pool, acquire some rssi data
   * need some rssi logger app. Did not find something meaningful
1. beautifications: add DFU interface to dongle setup? (Nordic DFU Trigger Interface)
1. get the taiyo yuden running (see [adaptions](#Taiyo-Yuden-adaptions) )   
   need the s112? Maybe nRF5SDK16\ble_app_beacon\pca10056e\s112\ses or nRF5SDK**15**\nrf52-ble-tutorial-advertising\pca10040e\s112\ses

# Done
1. widmedia.ch/swim page. (SwimMeter, swimmeter, swim-meter etc)... must not be more than 17chars: . /swim is the main page, others just forwardings. SwimMeter however shall be the main name
1. Mobile (Galaxy S6) apparently only has bluetooth 4.1. should be enough though to receive any beacon variety 
1. laptop: segger license (hooked to bluetooth connection, not ideal)
1. [nRF command line tools](https://www.nordicsemi.com/Software-and-Tools/Development-Tools/nRF-Command-Line-Tools/Download#infotabs)
1. not doing it, working with other examples: ~~port the ble-tutorial-advertising to SDK16. Understand the code of this example~~

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
 <!--- ## Nordicsemi Code --->

## Taiyo Yuden adaptions
example code about the 32 kHz crystal osc: page 27 in [NZWW data report](https://www.yuden.co.jp/wireless_module/document/datareport2/en/TY_BLE_EYSLSNZWW_DataReport_V1_0_20190227E.pdf)
From FQA: _each BLE module has an internal 32MHz crystal. Please note, Nordic's nRF51DK (evaluation board) and nRF51 sample applications included in SDK are designed to run on a 16MHz clock. Since TAIYO YUDEN modules run on a 32MHz clock, Nordic's nRF51 sample applications will need some modification in order for it to work on TAIYO YUDEN modules._

_To fix this issue, we need to write the value 0xFFFFFF00 to the UICR (User Information Configuration Register) at address 0x10001008. Please note that the UICR is erased whenever you download a SoftDevice._ 
 
_The UICR can be written by using the debug tools:
nrfjprog.exe --snr <your_jlink_debugger_serial_number> --memwr 0x10001008 --val 0xFFFFFF00_ 
 
_Or the following code can be added to the SystemInit function in the system_nRF51.c file, right 
before launching the TASK_HFCLKSTART task:_

```
if (*(uint32_t *)0x10001008 == 0xFFFFFFFF)  
{ 
    NRF_NVMC->CONFIG = NVMC_CONFIG_WEN_Wen << NVMC_CONFIG_WEN_Pos;  
    while (NRF_NVMC->READY == NVMC_READY_READY_Busy){}  
    *(uint32_t *)0x10001008 = 0xFFFFFF00;  
    NRF_NVMC->CONFIG = NVMC_CONFIG_WEN_Ren << NVMC_CONFIG_WEN_Pos;  
    while (NRF_NVMC->READY == NVMC_READY_READY_Busy){}   
    NVIC_SystemReset();  
    while (true){}  
}  
```
Defines are available in the sdk_config.h. Also I guess I need the S112 soft device [see here](https://devzone.nordicsemi.com/f/nordic-q-a/39981/nrf52810-taiyo-yuden-eyslcnzww-problem-with-nrfgo-studio). Flush that one nRFGo?

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

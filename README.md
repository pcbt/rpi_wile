# rpi_wile
Raspberry Pi WiFi configuration app via BLE


## Required Libraries

### bluez 5.49 or above (tested on 5.49, higher versions will probably work)

```
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.49.tar.xz
tar xvf bluez-5.49.tar.xz
```
```
sudo apt-get update
sudo apt-get install -y libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
```
```
cd bluez-5.49
./configure
make
sudo make install
```
### systemd for running as a service

move airchip.service file to /etc/systemd/system

```
sudo chmod a+x busad.service
sudo chmod a+x bus_ad.py
```

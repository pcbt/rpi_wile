import dbus
import dbus.mainloop.glib
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import ssl
import subprocess
import sys
import os
import wifi_lib as wl

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject



from bluez import *

mainloop = None

auth = {
  'username':"airchip1",
  'password':"yildiz2013"
}

tls = {
  'ca_certs':"/etc/ssl/certs/ca-certificates.crt",
}

def ssid_scan():
    try:

        res = subprocess.Popen(["sudo iwlist wlan0 scan | grep ESSID"], stdout=subprocess.PIPE, shell=True)

        (out, err) = res.communicate()


        if out:
            print("OK> SSID scan is complete; return code> " + str(res.returncode))
        if err:
            print ("ret> "+str(res.returncode))
            print ("Error> error while scanning SSIDs!! "+err.strip())

    except OSError as e:
        print ("OSError > ",e.errno)
        print ("OSError > ",e.strerror)
        print ("OSError > ",e.filename)

    except:
        print ("Error > ",sys.exc_info()[0])

    out2=out.decode("UTF-8").split("ESSID:")
    out3=out2[1].split("\n")[0].encode("UTF-8")
    print(out3)
    return out3



class SSIDScanner(Characteristic):
    """
    SSID scanner characteristic. Scans the available SSIDs and return back to user. Get SSID password
    from user and configure the Raspberry wpa_supplicant.conf file.

    """
    SSID_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef2'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.SSID_CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []

    def WifiScanner(self):
        ssid_list=[]
        values = wl.Search()
        if values is not None:
            print("Wifi SSIDs are scanned")
            for i in values:
                print("SSID: " + i.ssid)
                ssid_list.append(i.ssid.encode('UTF-8'))
                # value.append(dbus.Byte(0x06))
                # value.append(dbus.Byte(i.ssid.encode('utf-8')))
        return ssid_list

    def ReadValue(self, options):
        self.value = 3
        # self.value = WifiScanner()
        print("Data reading from Center BLE Device" + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print("Sending data from Center BLE Device to Server" + repr(value))
        publish.single("test",payload=str(value),hostname="mqtt.airchip.com.tr",client_id="bus1",auth=auth,tls=tls,port=8883,protocol=mqtt.MQTTv311)
        self.value = value


class MqttMessage(Characteristic):
    """
    Dummy test characteristic. Allows writing arbitrary bytes to its value, and
    contains "extended properties", as well as a test descriptor.

    """
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef1'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []

    def ReadValue(self, options):
        print("Data reading from Center BLE Device" + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print("Sending data from Center BLE Device to Server" + repr(value))
        publish.single("test",payload=str(value),hostname="mqtt.airchip.com.tr",client_id="bus1",auth=auth,tls=tls,port=8883,protocol=mqtt.MQTTv311)
        self.value = value

class SSIDService(Service):
    SSID_SRV_UUID = '12345678-1234-5678-1234-56789abc0020'
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.SSID_SRV_UUID, True)
        self.add_characteristic(SSIDScanner(bus, 0, self))


class BusService(Service):
    BUS_SRV_UUID = '12345678-1234-5678-1234-56789abc0010'
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.BUS_SRV_UUID, True)
        self.add_characteristic(MqttMessage(bus, 0, self))

class BusApplication(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(SSIDService(bus, 0))



class BusAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(SSIDService.SSID_SRV_UUID)

        self.include_tx_power = True

def register_ad_cb():
    """
    Callback if registering advertisement was successful
    """
    print('Advertisement registered')


def register_ad_error_cb(error):
    """
    Callback if registering advertisement failed
    """
    print('Failed to register advertisement: ' + str(error))
    mainloop.quit()


def register_app_cb():
    """
    Callback if registering GATT application was successful
    """
    print('GATT application registered')


def register_app_error_cb(error):
    """
    Callback if registering GATT application failed.
    """
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def main():
    global mainloop
    global display

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    # Get ServiceManager and AdvertisingManager
    service_manager = get_service_manager(bus)




    ad_manager = get_ad_manager(bus)




    # Create gatt services
    app = BusApplication(bus)

    # Create advertisement
    test_advertisement = BusAdvertisement(bus, 0)

    mainloop = GObject.MainLoop()

    # Register gatt services
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)


    # Register advertisement
    ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        display.clear()
        display.write_display()


if __name__ == '__main__':
    main()

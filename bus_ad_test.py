#!/usr/bin/env python3
import dbus
import dbus.mainloop.glib
import ssl
import subprocess
import sys
import os
import datetime
import time

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

from bluez_lib import *
from mqtt_lib import *

mainloop = None

ble_password = '5860'

auth = {
  'username':"airchip1",
  'password':"yildiz2013"
}

tls = {
  'ca_certs':"/etc/ssl/certs/ca-certificates.crt",
}

def reboot():
    cmd = 'sudo reboot'
    cmd_result = os.system(cmd)
    print(cmd_result)



def wpa_file(ssid,psk):
    # write wifi config to file
    f = open('wifi.conf', 'w')
    f.write('country=GB\n')
    f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
    f.write('update_config=1\n')
    f.write('\n')
    f.write('network={\n')
    f.write('    ssid="' + ssid + '"\n')
    f.write('    psk="' + psk + '"\n')
    f.write('}\n')
    f.close()

    wpa_supplicant_conf = "/etc/wpa_supplicant/wpa_supplicant.conf"
    sudo_mode = 'sudo '



    try:

        res = subprocess.Popen(['sudo mv wifi.conf ' + wpa_supplicant_conf], stdout=subprocess.PIPE, shell=True)

        (out, err) = res.communicate()


        if out:
            print("OK> wpa_supplicant file copied; return code> " + str(res.returncode))
        if err:
            print ("ret> "+str(res.returncode))
            print ("Error> error while wpa_supplicant file copying!! "+err.strip())

    except OSError as e:
        print ("OSError > ",e.errno)
        print ("OSError > ",e.strerror)
        print ("OSError > ",e.filename)

    except:
        print ("Error > ",sys.exc_info()[0])



def local_ip_adress():
    ip_address = "<Not Set>"

    try:
        p = subprocess.Popen(['ifconfig', 'wlan0'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        out, err = p.communicate()

        if out:
            print("OK> Local IP address fetched; return code> " + str(res.returncode))
            for l in out.split('\n'):
                if l.strip().startswith("inet addr:"):
                    ip_address = l.strip().split(' ')[1].split(':')[1]

            return ip_address
        if err:
            print ("ret> "+str(res.returncode))
            print ("Error> error while fetching local IP address!! "+err.strip())


        except OSError as e:
            print ("OSError > ",e.errno)
            print ("OSError > ",e.strerror)
            print ("OSError > ",e.filename)

        except:
            print ("Error > ",sys.exc_info()[0])


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
    ssid_list=[]
    out=out.decode("UTF-8").split("ESSID:")
    for i in out:
        ssid_list.append(i.split("\n")[0].replace('"',''))

    ssid_list.reverse()
    ssid_list.pop()
    ssid_list.reverse()
    print(ssid_list)
    return ssid_list

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
        self.ssid_list = []
        self.list_index = 0
        self.service_password =''
        self.ssid_password=''
        self.local_ip_address='<Not Set>'

    def ReadValue(self, options):
        #print("Data reading from Center BLE Device " + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        if value is not None:
            if str(value[0]) is 'B':
                self.service_password=str(value[1])+str(value[2])+str(value[3])+str(value[4])
                print('B Pressed:BLE device password enterred! :'+self.service_password)
                reply = dbus.Array(signature='y')
                for i in "Password Enterred!":
                    reply.append(dbus.Byte(i.encode('utf-8')))
            elif self.service_password == ble_password:
                if str(value[0]) is 'S':
                    print('S Pressed:SSID scanning started! Function = ssid_scan()')
                    self.ssid_list = ssid_scan()
                    self.list_index = 0
                    reply = dbus.Array(signature='y')
                    print('SSID scan completed!')
                    for i in "SSID scanning is completed!":
                        reply.append(dbus.Byte(i.encode('utf-8')))


                elif str(value[0]) is 'N':

                    if self.ssid_list is None:
                        print('N Pressed:SSID list is empty!')
                        reply = dbus.Array(signature='y')
                        for i in "No SSID list!!":
                            reply.append(dbus.Byte(i.encode('utf-8')))

                    else:
                        print('N Pressed:SSID sent!')
                        reply = dbus.Array(signature='y')
                        for i in self.ssid_list[self.list_index]:
                            reply.append(dbus.Byte(i.encode('utf-8')))
                        print('Sent SSID:'+self.ssid_list[self.list_index])
                        self.list_index = self.list_index +1
                elif str(value[0]) is 'P':
                    print('P Pressed:SSID password entered!')
                    ssid_key=''
                    for i in range(1,len(value)):
                        ssid_key+=str(value[i])
                    self.ssid_password=ssid_key
                    print('SSID key: '+ssid_key)
                    self.value=value

                elif str(value[0]) is 'C':
                    if self.ssid_list is None:
                        print('C Pressed:SSID list is empty!')
                        reply = dbus.Array(signature='y')
                        for i in "No SSID list!!":
                            reply.append(dbus.Byte(i.encode('utf-8')))
                    else:
                        print('C Pressed:SSID and Password: '+self.ssid_list[int(str(value[1]))]+' '+self.ssid_password)
                        ip_address=wpa_file(self.ssid_list[int(str(value[1]))],self.ssid_password)
                        print('IP Adress :'+ip_address)
                        reply = dbus.Array(signature='y')
                        return_txt="SSID added to wpa_supplicant file!! IP: "+str(ip_address)
                        for i in return_txt:
                            reply.append(dbus.Byte(i.encode('utf-8')))
                elif str(value[0]) is 'R':
                    print('R Pressed:Rebooting!!')
                    reply = dbus.Array(signature='y')
                    for i in "Rebooting!":
                        reply.append(dbus.Byte(i.encode('utf-8')))
                    reboot()
                elif str(value[0]) is 'L':
                    print('L Pressed:Getting device local IP address!!')
                    reply = dbus.Array(signature='y')
                    self.local_ip_address=local_ip_adress()
                    for i in self.local_ip_address:
                        reply.append(dbus.Byte(i.encode('utf-8')))



            else:
                reply = dbus.Array(signature='y')
                for i in "Password Incorrect!":
                    reply.append(dbus.Byte(i.encode('utf-8')))



        self.value = reply


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

    # mqttc = mqtt.Client()
    # mqttc.on_message = on_message
    # mqttc.on_connect = on_connect
    # mqttc.on_publish = on_publish
    # mqttc.on_subscribe = on_subscribe
    # # Uncomment to enable debug messages
    # # mqttc.on_log = on_log
    # mqttc.connect("mqtt.airchip.com.tr", 8883, 60)
    # mqttc.subscribe("bus/ble/password", 2)
    #
    # mqttc.loop_forever()
    #

    try:

        mainloop.run()
    except KeyboardInterrupt:
        display.clear()
        display.write_display()


if __name__ == '__main__':
    main()

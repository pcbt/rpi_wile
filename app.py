#!/usr/bin/env python3
import dbus
import dbus.mainloop.glib
import ssl
import subprocess
import sys
import os
import datetime
import time
import logging
import threading

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

from bluez_lib import *


mainloop = None

ble_password = '5860'


def disconnect_timer():
    def timer_target():
        print('Disconnecting in 3 mins!')
        logging.info('Disconnecting in 3 mins!')
        time.sleep(180)
        disconnect_device()

    thread = threading.Thread(target=timer_target)
    thread.daemon = True
    thread.start()


def disconnect_device():
    try:
        res = subprocess.Popen(['bluetoothctl', 'disconnect'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        out, err = res.communicate()

        if out:
            print("OK> Device Disconnected After 3 min! " + str(res.returncode))

            logging.info("OK> Device Disconnected After 3 min! " + str(res.returncode))


        if err:
            print ("ret> "+str(res.returncode))
            print ("Error> error while disconnecting bl device "+err.strip())



            logging.error ("ret> "+str(res.returncode))
            logging.error ("Error> error while disconnecting bl device "+err.strip())


    except OSError as e:
        print ("OSError > ",e.errno)
        print ("OSError > ",e.strerror)
        print ("OSError > ",e.filename)

        logging.error ("OSError > ",e.errno)
        logging.error ("OSError > ",e.strerror)
        logging.error ("OSError > ",e.filename)

    except:
        print ("Error > ",sys.exc_info()[0])

        logging.error ("Error > ",sys.exc_info()[0])

def property_changed(interface, changed, invalidated, path):
    iface = interface[interface.rfind('.')+1:]
    for name, value in changed.items():
        val = str(value)
        if str(name) == "Connected" and val == "1":
            print("Device Connected! Path : "+path)
            logging.info("Device Connected! Path : "+path)
            disconnect_timer()
        elif str(name) == "Connected" and val == "0":
            print("Device Disconnected! Path : "+path)
            logging.info("Device Disconnected! Path : "+path)
        else:
            print("{%s.PropertyChanged} [%s] %s = %s" % (iface, path, name,val))
            logging.info("{%s.PropertyChanged} [%s] %s = %s" % (iface, path, name,val))


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

            logging.info("OK> wpa_supplicant file copied; return code> " + str(res.returncode))

        if err:
            print ("ret> "+str(res.returncode))
            print ("Error> error while wpa_supplicant file copying!! "+err.strip())

            logging.error ("ret> "+str(res.returncode))
            logging.error ("Error> error while wpa_supplicant file copying!! "+err.strip())

    except OSError as e:
        print ("OSError > ",e.errno)
        print ("OSError > ",e.strerror)
        print ("OSError > ",e.filename)

        logging.error ("OSError > ",e.errno)
        logging.error ("OSError > ",e.strerror)
        logging.error ("OSError > ",e.filename)

    except:
        print ("Error > ",sys.exc_info()[0])

        logging.error ("Error > ",sys.exc_info()[0])



def local_ip_adress():
    ip_address = "<Not Set>"

    try:
        res = subprocess.Popen(['ifconfig', 'wlan0'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        out, err = res.communicate()

        if out:
            print("OK> Local IP address fetched; return code> " + str(res.returncode))

            logging.info("OK> Local IP address fetched; return code> " + str(res.returncode))

            ip_address = out.decode('UTF-8').split('inet')[1][1:-10]
            return ip_address
        if err:
            print ("ret> "+str(res.returncode))
            print ("Error> error while fetching local IP address!! "+err.strip())

            ip_address = "Error> error while fetching local IP address!! "

            logging.error ("ret> "+str(res.returncode))
            logging.error ("Error> error while fetching local IP address!! "+err.strip())


    except OSError as e:
        print ("OSError > ",e.errno)
        print ("OSError > ",e.strerror)
        print ("OSError > ",e.filename)

        logging.error ("OSError > ",e.errno)
        logging.error ("OSError > ",e.strerror)
        logging.error ("OSError > ",e.filename)

    except:
        print ("Error > ",sys.exc_info()[0])

        logging.error ("Error > ",sys.exc_info()[0])


def ssid_scan():
    ssid_list=[]
    try:

        res = subprocess.Popen(["sudo iwlist wlan0 scan | grep ESSID"], stdout=subprocess.PIPE, shell=True)

        (out, err) = res.communicate()


        if out:
            print("OK> SSID scan is complete; return code> " + str(res.returncode))

            logging.info("OK> SSID scan is complete; return code> " + str(res.returncode))

            for i in out.decode("UTF-8").split("ESSID:"):
                ssid_list.append(i.split("\n")[0].replace('"',''))

            ssid_list.reverse()
            ssid_list.pop()
            ssid_list.reverse()
            print(ssid_list)
            return ssid_list

        if err:
            print ("ret> "+str(res.returncode))
            print ("Error> error while scanning SSIDs!! "+err.strip())

            logging.error ("ret> "+str(res.returncode))
            logging.error ("Error> error while scanning SSIDs!! "+err.strip())

    except OSError as e:
        print ("OSError > ",e.errno)
        print ("OSError > ",e.strerror)
        print ("OSError > ",e.filename)

        logging.error ("OSError > ",e.errno)
        logging.error ("OSError > ",e.strerror)
        logging.error ("OSError > ",e.filename)

    except:
        print ("Error > ",sys.exc_info()[0])

        logging.error ("Error > ",sys.exc_info()[0])


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

                logging.info('B Pressed:BLE device password enterred! :'+self.service_password)

                reply = dbus.Array(signature='y')
                for i in "Password Enterred!":
                    reply.append(dbus.Byte(i.encode('utf-8')))
            elif self.service_password == ble_password:
                if str(value[0]) is 'S':
                    print('S Pressed:SSID scanning started! Function = ssid_scan()')

                    logging.info('S Pressed:SSID scanning started! Function = ssid_scan()')

                    self.ssid_list = ssid_scan()
                    self.list_index = 0
                    reply = dbus.Array(signature='y')
                    print('SSID scan completed!')

                    logging.info('SSID scan completed!')

                    for i in "SSID scanning is completed!":
                        reply.append(dbus.Byte(i.encode('utf-8')))


                elif str(value[0]) is 'N':

                    if self.ssid_list is None:
                        print('N Pressed:SSID list is empty!')

                        logging.warning('N Pressed:SSID list is empty!')

                        reply = dbus.Array(signature='y')
                        for i in "No SSID list!!":
                            reply.append(dbus.Byte(i.encode('utf-8')))

                    else:
                        print('N Pressed:SSID sent!')

                        logging.info('N Pressed:SSID sent!')

                        reply = dbus.Array(signature='y')
                        for i in self.ssid_list[self.list_index]:
                            reply.append(dbus.Byte(i.encode('utf-8')))
                        print('Sent SSID:'+self.ssid_list[self.list_index])

                        logging.info('Sent SSID:'+self.ssid_list[self.list_index])

                        self.list_index = self.list_index +1
                elif str(value[0]) is 'P':
                    print('P Pressed:SSID password entered!')

                    logging.info('P Pressed:SSID password entered!')

                    ssid_key=''
                    for i in range(1,len(value)):
                        ssid_key+=str(value[i])
                    self.ssid_password=ssid_key
                    print('SSID key: '+ssid_key)

                    logging.info('SSID key: '+ssid_key)

                    self.value=value

                elif str(value[0]) is 'C':
                    if self.ssid_list is None:
                        print('C Pressed:SSID list is empty!')

                        logging.warning('C Pressed:SSID list is empty!')

                        reply = dbus.Array(signature='y')
                        for i in "No SSID list!!":
                            reply.append(dbus.Byte(i.encode('utf-8')))
                    else:
                        print('C Pressed:SSID and Password: '+self.ssid_list[int(str(value[1]))]+' '+self.ssid_password +'Function: wpa_file()')

                        logging.info('C Pressed:SSID and Password: '+self.ssid_list[int(str(value[1]))]+' '+self.ssid_password +'Function: wpa_file()')

                        wpa_file(self.ssid_list[int(str(value[1]))],self.ssid_password)




                        reply = dbus.Array(signature='y')

                        for i in "SSID added to wpa_supplicant file!!":
                            reply.append(dbus.Byte(i.encode('utf-8')))

                        print('Wpa file copied succesfully')

                        logging.info('Wpa file copied succesfully')

                elif str(value[0]) is 'R':
                    print('R Pressed:Rebooting!!')

                    logging.info('R Pressed:Rebooting!!')

                    reply = dbus.Array(signature='y')
                    for i in "Rebooting!":
                        reply.append(dbus.Byte(i.encode('utf-8')))
                    reboot()
                elif str(value[0]) is 'L':
                    print('L Pressed:Getting device local IP address!!')

                    logging.info('L Pressed:Getting device local IP address!!')

                    reply = dbus.Array(signature='y')
                    self.local_ip_address=local_ip_adress()
                    for i in self.local_ip_address:
                        reply.append(dbus.Byte(i.encode('utf-8')))

                elif str(value[0]) is 'D':
                    print('D Pressed:Deleting Local Cache!!')
                    logging.info('D Pressed:Deleting Local Cache!!')
                    self.value = []
                    self.ssid_list = []
                    self.list_index = 0
                    self.service_password =''
                    self.ssid_password=''
                    print("Service values are cleared!")
                    logging.info("Service values are cleared!")




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
    logging.info('Advertisement registered')


def register_ad_error_cb(error):
    """
    Callback if registering advertisement failed
    """
    print('Failed to register advertisement: ' + str(error))
    logging.error('Failed to register advertisement: ' + str(error))
    mainloop.quit()


def register_app_cb():
    """
    Callback if registering GATT application was successful
    """
    print('GATT application registered')
    logging.info('GATT application registered')


def register_app_error_cb(error):
    """
    Callback if registering GATT application failed.
    """
    print('Failed to register application: ' + str(error))
    logging.error('Failed to register application: ' + str(error))
    mainloop.quit()


def main():
    global mainloop
    global display

    logging.info('Service started!')

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    # Get ServiceManager and AdvertisingManager
    service_manager = get_service_manager(bus)




    ad_manager = get_ad_manager(bus)




    # Create gatt services
    app = BusApplication(bus)

    # Create advertisement
    airchip_advertisement = BusAdvertisement(bus, 0)

    bus.add_signal_receiver(property_changed, bus_name="org.bluez",
			dbus_interface="org.freedesktop.DBus.Properties",
			signal_name="PropertiesChanged",
			path_keyword="path")

    mainloop = GObject.MainLoop()

    # Register gatt services
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)


    # Register advertisement
    ad_manager.RegisterAdvertisement(airchip_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)



    mainloop.run()

if __name__ == '__main__':

    main()

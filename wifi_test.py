import subprocess
import sys
import os


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

for i in out2:
    print(i)

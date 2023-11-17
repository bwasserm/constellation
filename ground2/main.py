#!python

import sacn
import time
import collections

flags = collections.defaultdict(lambda _: (0, 0, 0, 0))
flags.update({
    23: [
        (255, 0, 0, 0),
        (0, 255, 0, 0),
        (0, 0, 255, 0),
    ]
})

# 60:01:94:22:20:83


def main():
    sender = sacn.sACNsender('192.168.1.4')  # provide an IP-Address to bind to if you want to send multicast packets from a specific interface
    sender.start()  # start the sending thread
    sender.activate_output(1)  # start sending out data in the 1st universe
    sender[1].multicast = True  # set multicast to True
    # sender[1].destination = "192.168.1.20"  # or provide unicast information.
    # Keep in mind that if multicast is on, unicast is not used
    sender[1].dmx_data = ([0, 255, 0, 0] * 128)  # some test DMX data
    print(sender[1].dmx_data)

    # time.sleep(10)  # send the data for 10 seconds
    sender.stop()  # do not forget to stop the sender

if __name__ == '__main__':
    main()
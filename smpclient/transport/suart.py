# Copyright 2016 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Allow creation of uart/console interface via usb google serial endpoint."""

import array
import platform
import threading
from typing import Optional

import usb


class SusbError(Exception):
    """Class for exceptions of Susb."""

    def __init__(self, msg: str, value: int = 0):
        """SusbError constructor.

        Args:
          msg: string, message describing error in detail
          value: integer, value of error when non-zero status returned.  Default=0
        """
        super(SusbError, self).__init__(msg, value)
        self.msg = msg
        self.value = value


class Susb:
    """Provide USB functionality.

    Instance Variables:
    _read_ep: pyUSB read endpoint for this interface
    _write_ep: pyUSB write endpoint for this interface
    """

    READ_ENDPOINT = 0x81
    WRITE_ENDPOINT = 0x1
    TIMEOUT_MS = 2

    def __init__(
        self,
        vendor: int = 0x18D1,
        product: int = 0x500F,
        interface: int = 1,
        serialname: Optional[str] = None,
    ):
        """Susb constructor.

        Discovers and connects to USB endpoints.

        Args:
          vendor    : usb vendor id of device
          product   : usb product id of device
          interface : interface number ( 1 - 8 ) of device to use
          serialname: string of device serialnumber.

        Raises:
          SusbError: An error accessing Susb object
        """
        # Find the device.
        dev_g = usb.core.find(idVendor=vendor, idProduct=product, find_all=True)
        dev_list = list(dev_g)
        if dev_list is None:
            raise SusbError("USB device not found")

        # Check if we have multiple devices.
        dev = None
        if serialname:
            for d in dev_list:
                dev_serial = "PyUSB doesn't have a stable interface"
                try:
                    dev_serial = usb.util.get_string(d, 256, d.iSerialNumber)
                except:
                    dev_serial = usb.util.get_string(d, d.iSerialNumber)
                if dev_serial == serialname:
                    dev = d
                    break
            if dev is None:
                raise SusbError("USB device(%s) not found" % (serialname,))
        else:
            try:
                dev = dev_list[0]
            except:
                try:
                    dev = next(dev_list)
                except:
                    raise SusbError("USB device %04x:%04x not found" % (vendor, product))

        # If we can't set configuration, it's already been set.
        try:
            dev.set_configuration()
        except usb.core.USBError:
            pass

        # Get an endpoint instance.
        cfg = dev.get_active_configuration()
        intf = usb.util.find_descriptor(cfg, bInterfaceNumber=interface)
        self._intf = intf

        if not intf:
            raise SusbError("Interface not found")

        # Detach raiden.ko if it is loaded.
        if platform.system() != 'Darwin':
            if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                dev.detach_kernel_driver(intf.bInterfaceNumber)

        read_ep_number = intf.bInterfaceNumber + self.READ_ENDPOINT
        read_ep = usb.util.find_descriptor(intf, bEndpointAddress=read_ep_number)
        self._read_ep = read_ep

        write_ep_number = intf.bInterfaceNumber + self.WRITE_ENDPOINT
        write_ep = usb.util.find_descriptor(intf, bEndpointAddress=write_ep_number)
        self._write_ep = write_ep


"""Suart class implements a stream interface, to access Google's USB class.

  This creates a send and receive thread that monitors USB and console input
  and forwards them across. This particular class is hardcoded to stdin/out.
"""


class SuartError(Exception):
    """Class for exceptions of Suart."""

    def __init__(self, msg: str, value: int = 0):
        """SuartError constructor.

        Args:
          msg: string, message describing error in detail
          value: integer, value of error when non-zero status returned.  Default=0
        """
        super(SuartError, self).__init__(msg, value)
        self.msg = msg
        self.value = value


class Suart:
    """Provide interface to serial usb endpoint."""

    def __init__(
        self,
        vendor: int = 0x18D1,
        product: int = 0x501C,
        interface: int = 0,
        serialname: Optional[str] = None,
    ):
        """Suart contstructor.

        Initializes USB stream interface.

        Args:
          vendor: usb vendor id of device
          product: usb product id of device
          interface: interface number of device to use
          serialname: Defaults to None.

        Raises:
          SuartError: If init fails
        """
        self._done = threading.Event()
        self._susb = Susb(
            vendor=vendor, product=product, interface=interface, serialname=serialname
        )
        self.port: Optional[str] = None
        self.out_waiting = 0
        self._exit = False

    def write(self, data) -> int:
        self.out_waiting = len(data)
        out = self._susb._write_ep.write(data, self._susb.TIMEOUT_MS)
        self.out_waiting -= out
        return out

    # ll = len(data)
    # s = 0
    # while ll > 0:
    #     l_to_send = 64 if ll > 64 else ll
    #     _d = data[s:l_to_send]
    #     print(f"x:{l_to_send}")
    #     l_to_send = self._susb._write_ep.write(_d, self._susb.TIMEOUT_MS)
    #     ll -= l_to_send
    #     s += l_to_send
    #     print(l_to_send)
    # return s

    def read(self) -> Optional[array.array]:
        try:
            return self._susb._read_ep.read(64, self._susb.TIMEOUT_MS)
        except Exception as ex:
            return None

    def read_all(self) -> Optional[array.array]:
        return self.read()

    def close(self) -> None:
        print("Suart closed!!")

    def open(self) -> None:
        print("Suart opened!!")

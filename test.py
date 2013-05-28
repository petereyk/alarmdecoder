#!/usr/bin/env python

import pyad2usb.ad2usb
import time
import signal
import traceback
import sys

running = True

def signal_handler(signal, frame):
    global running

    running = False

def handle_open(sender, args):
    print 'O', args

def handle_close(sender, args):
    print 'C', args

def handle_read(sender, args):
    print '<', args

def handle_write(sender, args):
    print '>', args

def handle_attached(sender, args):
    print '+', args

def handle_detached(sender, args):
    print '-', args

def handle_power_changed(sender, args):
    print 'power changed', args

def handle_alarm_bell(sender, args):
    print 'alarm', args

def handle_bypass(sender, args):
    print 'bypass', args

def handle_message(sender, args):
    print args

def handle_firmware(stage):
    if stage == pyad2usb.ad2usb.util.Firmware.STAGE_START:
        handle_firmware.wait_tick = 0
        handle_firmware.upload_tick = 0
    elif stage == pyad2usb.ad2usb.util.Firmware.STAGE_WAITING:
        if handle_firmware.wait_tick == 0:
            sys.stdout.write('Waiting for device.')
        handle_firmware.wait_tick += 1

        sys.stdout.write('.')
        sys.stdout.flush()
    elif stage == pyad2usb.ad2usb.util.Firmware.STAGE_BOOT:
        if handle_firmware.wait_tick > 0: print ""
        print "Rebooting device.."
    elif stage == pyad2usb.ad2usb.util.Firmware.STAGE_LOAD:
        print 'Waiting for boot loader..'
    elif stage == pyad2usb.ad2usb.util.Firmware.STAGE_UPLOADING:
        if handle_firmware.upload_tick == 0:
            sys.stdout.write('Uploading firmware.')

        handle_firmware.upload_tick += 1

        if handle_firmware.upload_tick % 30 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
    elif stage == pyad2usb.ad2usb.util.Firmware.STAGE_DONE:
        print "\r\nDone!"

def upload_usb():
    dev = pyad2usb.ad2usb.devices.USBDevice()

    dev.open(no_reader_thread=True)
    pyad2usb.ad2usb.util.Firmware.upload(dev, 'tmp/ademcoemu_V2_2a_6.hex', handle_firmware)
    dev.close()

def upload_serial():
    dev = pyad2usb.ad2usb.devices.SerialDevice(interface='/dev/ttyUSB0')

    dev.open()
    pyad2usb.ad2usb.util.Firmware.upload(dev, 'tmp/ademcoemu_V2_2a_6.hex', handle_firmware)
    dev.close()

def upload_usb_serial():
    dev = pyad2usb.ad2usb.devices.SerialDevice(interface='/dev/ttyUSB5')

    dev.open(baudrate=115200)
    pyad2usb.ad2usb.util.Firmware.upload(dev, 'tmp/ademcoemu_V2_2a_6.hex', handle_firmware)
    dev.close()

def upload_socket():
    dev = pyad2usb.ad2usb.devices.SocketDevice(interface=('localhost', 10000))

    dev.open()
    pyad2usb.ad2usb.util.Firmware.upload(dev, 'tmp/ademcoemu_V2_2a_6.hex', handle_firmware)
    dev.close()

def test_usb():
    dev = pyad2usb.ad2usb.devices.USBDevice()

    a2u = pyad2usb.ad2usb.AD2USB(dev)
    a2u.on_open += handle_open
    a2u.on_close += handle_close
    a2u.on_read += handle_read
    a2u.on_write += handle_write

    a2u.on_power_changed += handle_power_changed
    a2u.on_alarm += handle_alarm_bell
    a2u.on_bypass += handle_bypass

    a2u.open()

    print dev._id

    while running:
        time.sleep(0.1)

    a2u.close()

def test_serial():
    dev = pyad2usb.ad2usb.devices.SerialDevice(interface='/dev/ttyUSB0')

    a2u = pyad2usb.ad2usb.AD2USB(dev)
    a2u.on_open += handle_open
    a2u.on_close += handle_close
    a2u.on_read += handle_read
    a2u.on_write += handle_write

    a2u.open()

    print dev._id

    while running:
        time.sleep(0.1)

    a2u.close()

def test_usb_serial():
    dev = pyad2usb.ad2usb.devices.SerialDevice(interface='/dev/ttyUSB5')

    a2u = pyad2usb.ad2usb.AD2USB(dev)
    a2u.on_open += handle_open
    a2u.on_close += handle_close
    a2u.on_read += handle_read
    a2u.on_write += handle_write

    a2u.open(baudrate=115200)
    print dev._id

    while running:
        time.sleep(0.1)

    a2u.close()

def test_factory():
    a2u = pyad2usb.ad2usb.Overseer.create()

    a2u.on_open += handle_open
    a2u.on_close += handle_close
    a2u.on_read += handle_read
    a2u.on_write += handle_write

    a2u.open()

    while running:
        time.sleep(0.1)

    a2u.close()

def test_factory_watcher():
    overseer = pyad2usb.ad2usb.Overseer(attached_event=handle_attached, detached_event=handle_detached)

    a2u = overseer.get_device()

    a2u.on_open += handle_open
    a2u.on_close += handle_close
    a2u.on_read += handle_read
    a2u.on_write += handle_write

    a2u.open()

    while running:
        time.sleep(0.1)

    a2u.close()
    overseer.close()

def test_socket():
    dev = pyad2usb.ad2usb.devices.SocketDevice(interface=("localhost", 10000))

    a2u = pyad2usb.ad2usb.AD2USB(dev)
    a2u.on_open += handle_open
    a2u.on_close += handle_close
    #a2u.on_read += handle_read
    #a2u.on_write += handle_write

    a2u.on_message += handle_message
    a2u.on_power_changed += handle_power_changed
    a2u.on_alarm += handle_alarm_bell
    a2u.on_bypass += handle_bypass

    a2u.open()

    print dev._id

    while running:
        time.sleep(0.1)

    a2u.close()

def test_no_read_thread():
    a2u = pyad2usb.ad2usb.Overseer.create()

    a2u.on_open += handle_open
    a2u.on_close += handle_close
    a2u.on_read += handle_read
    a2u.on_write += handle_write

    a2u.open(no_reader_thread=True)

    print 'alive?', a2u._device._read_thread.is_alive()

    a2u.close()

try:
    signal.signal(signal.SIGINT, signal_handler)

    #test_serial()
    #upload_serial()

    #test_usb()
    #test_usb_serial()
    #test_factory()
    #test_factory_watcher()
    upload_usb()
    #upload_usb_serial()

    #test_socket()
    #upload_socket()

    #test_no_read_thread()

except Exception, err:
    traceback.print_exc(err)

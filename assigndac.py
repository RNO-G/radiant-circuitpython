import digitalio
import busio
import board
import os

def getaddrs():
	ver = ord(os.uname()[4][30:31])-48
	if ver==1:
		return bytes([0x20,0x24,0x22,0x26,0x21,0x25])
	else:
		return bytes([0x38,0x3C,0x3A,0x3E,0x39,0x3D])

def setup():
	addrs = getaddrs()
	for addr in addrs:
		bistmode(addr, False)
	del addrs		

def assign():
	addrs = getaddrs()
	base = 0x62
	for addr in addrs:
		assignDac(addr, base)
		base = base + 1

def start(sda, scl):
	sda.value = True
	scl.value = True
	sda.value = False

def stop(sda, scl):
	scl.value = True
	sda.value = False
	sda.value = True

def pulse(scl):
	scl.value = True
	scl.value = False

def clock8(val, sda, scl):
	scl.value = False
	for i in range(8):
		if val & 0x80:
			sda.value = True
		else:
			sda.value = False
		pulse(scl)
		val <<= 1

def bistmode(gpioAddr, mode=False):
	if mode:
		val = 0x0C
	else:
		val = 0x08
	i2c = busio.I2C(board.SCL, board.SDA)
	i2c.try_lock()
	i2c.writeto(gpioAddr, bytes([0x01, val]), stop=True)
	i2c.writeto(gpioAddr, bytes([0x03, 0xC0]), stop=True)
	i2c.unlock()
	i2c.deinit()
	del i2c
	del val

def assignDac(gpioaddr, newDacAddr):
	bistmode(gpioaddr, True)
	assignDacSequence(newDacAddr)
	bistmode(gpioaddr, False)
	
def assignDacSequence(newDacAddr, oldDacAddr=0x60):
	newDacAddr &= 0x7
	newDacAddr <<= 2
	newDacAddr |= 0x62
	oldDacAddr <<= 1
	mosi = digitalio.DigitalInOut(board.MOSI)
	mosi.switch_to_output(value=True)
	sda = digitalio.DigitalInOut(board.SDA)
	scl = digitalio.DigitalInOut(board.SCL)
	sda.switch_to_output(value=True, drive_mode=digitalio.DriveMode.OPEN_DRAIN)
	scl.switch_to_output(value=True, drive_mode=digitalio.DriveMode.OPEN_DRAIN)
	start(sda, scl)
	clock8(oldDacAddr, sda, scl)
	sda.value = True
	pulse(scl)
	oldDacAddr &= 0xE
	oldDacAddr <<= 1
	oldDacAddr |= 0x61
	clock8(oldDacAddr, sda, scl)
	mosi.value = False
	sda.value = True
	pulse(scl)
	clock8(newDacAddr, sda, scl)
	sda.value = True
	pulse(scl)
	newDacAddr |= 0x1
	clock8(newDacAddr, sda, scl)
	sda.value = True
	pulse(scl)
	stop(sda, scl)	
	mosi.deinit()
	scl.deinit()
	sda.deinit()
	del mosi
	del scl
	del sda

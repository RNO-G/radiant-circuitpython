from adafruit_mcp230xx.xra1200 import XRA1200
from digitalio import DigitalInOut
import analogio
import os
import time
import board

class RadGPIO:
	def __init__(self, i2c, sclk, mosi):
		# I hate this, fix this later
		ver = ord(os.uname()[4][30:31])-48
		if ver == 1:
			base = 0x20
		else:
			base = 0x38
		self.quad = ( XRA1200(i2c, base | 0x0, 0xC0, 0x00),
		              XRA1200(i2c, base | 0x4, 0xC0, 0x00),
					  XRA1200(i2c, base | 0x2, 0xC0, 0x00),
					  XRA1200(i2c, base | 0x6, 0xC0, 0x00),
					  XRA1200(i2c, base | 0x1, 0xC0, 0x00),
					  XRA1200(i2c, base | 0x5, 0xC0, 0x00) )
		self.siggen = XRA1200(i2c, base | 0x3, 0x80, 0x28)
		self.sclk = DigitalInOut(sclk)
		self.mosi = DigitalInOut(mosi)
		self.sclk.switch_to_output(value=False)
		self.mosi.switch_to_output(value=False)		

	def atten(self, quadno, addr, val):
		toWrite = addr << 8
		toWrite |= val
		for i in range(16):
			self.mosi.value = toWrite & 0x1
			self.sclk.value = 1
			self.sclk.value = 0
			toWrite >>= 1
		self.quad[quadno].get_pin(1).value = 1
		self.quad[quadno].get_pin(1).value = 0

	def bist(self, quadno, mode):
		self.quad[quadno].get_pin(2).value = mode

	def bistmon(self, quadno, monsig=False):
		min = 0 if quadno < 4 else 3
		max = 3 if quadno < 4 else 6
		for i in range(min, max):
			self.bist(i, True)
			if quadno == i:
				self.quad[i].get_pin(1).value = 1
				self.quad[i].get_pin(3).value = monsig
			else:
				self.quad[i].get_pin(1).value = 0
				self.quad[i].get_pin(3).value = 0
		time.sleep(0.2)
		if quadno < 4:
			p = analogio.AnalogIn(board.LQ)
		else:
			p = analogio.AnalogIn(board.RQ)
		val = p.value
		self.quad[quadno].get_pin(1).value = 0
		self.quad[quadno].get_pin(3).value = 0
		for i in range(min, max):
			self.bist(i, False)
		p.deinit()
		del p
		del i
		del min
		del max		
		return val					
		
	def cal(self, quadno, mode):
		self.quad[quadno].get_pin(0).value = mode
		
	def latch(self, quadno):
		self.quad[quadno].get_pin(1).value = 1
		self.quad[quadno].get_pin(1).value = 0

	def lab(self, quadno, mode):
		if mode:
			self.quad[quadno].get_pin(5).value = 1
		else:
			self.quad[quadno].get_pin(5).value = 0
	
	def trig(self, quadno, mode):
		if mode:
			self.quad[quadno].get_pin(4).value = 1
		else:
			self.quad[quadno].get_pin(4).value = 0

	def siglatch(self):
		self.siggen.get_pin(1).value = 1
		self.siggen.get_pin(1).value = 0
	
	def sigen(self, mode):
		self.siggen.get_pin(6).value = mode
	
	def sigpulse(self, mode):
		if mode:
			self.siggen.get_pin(5).value = 0
			self.siggen.get_pin(4).value = 1
		else:
			self.siggen.get_pin(4).value = 0
			self.siggen.get_pin(5).value = 1
	
	def sigfil(self, mode):
		f0 = mode & 0x1
		f1 = mode & 0x2
		self.siggen.get_pin(0).value = f0
		self.siggen.get_pin(2).value = f1
		self.siggen.get_pin(3).value = not f1		

from micropython import const
import binascii
import gc
import time
import os


class RadClock:
	def __init__(self, i2c):
		self.dev = i2c	
		ver = ord(os.uname()[4][30:31])-48
		if ver == 1:
			self.addr = const(0x71)
		else:
			self.addr = const(0x70)
		while not self.dev.try_lock():
			pass
		self.dev.writeto(self.addr, bytes([0xFF,0x0]), stop=True)
		self.dev.unlock()
		self.page = 0

	def configure(self, fn):
		# TODO: properly catch it if it's not there
		data = open(fn, "rb")
		# disable outputs
		self.read_modify_write(230, 0x10, 0x10)
		# pause LOL. No read-modify-write because the 0x65 gets written later,
		# I guess.
		self.write(241, 0x80)
		# load configuration
		self.load(data)
		# 'Validate input clock status'
		# TODO: abandon if the clock's not there for a while
		val = 4
		while val & 0x4:
			val = self.read(218)
		# 'Configure PLL for locking'
		self.read_modify_write(49, 0x00, 0x80)
		# 'Initiate locking of PLL'
		self.read_modify_write(246, 0x2, 0x2)
		# 'Wait 25 ms'
		time.sleep(0.025)
		# 'Restart LOL' - write magic 0x65. this already has bit 7 = 0
		self.write(241, 0x65)
		# 'Confirm PLL Lock Status'
		# TODO: abandon if it doesn't lock for a while
		val = 0x11
		while val & 0x11:
			val = self.read(218)
		# 'Copy FCAL registers'
		# 237[1:0] to 47[1:0]
		val = self.read(237)
		val &= 0x3
		self.read_modify_write(47, val, 0x3)		
		# 236 to 46
		val = self.read(236)
		self.write(46, val)
		# 235 to 45
		val = self.read(235)
		self.write(45, val)
		# set 47 [7:2] to 000101b (0x14 = 000101b << 2)
		self.read_modify_write(47, 0x14, 0xFC)
		# 'Set PLL to use FCAL values'
		self.read_modify_write(49, 0x80, 0x80)
		# Not using down-spread
		# Enable outputs
		self.read_modify_write(230, 0x00, 0x10)

		data.close()
		print("Clock configuration complete")
		del data
		del val
		gc.collect()
		
	def load(self, data):	
		# always start on page 0, the configuration file
		# based on the C header modifies the page itself
		# we'll end on page 0 then too
		self.setPage(0)
		ln = data.readline()				
		while ln:
			valconv = binascii.unhexlify(ln[0:6])
			reg = valconv[0]
			val = valconv[1]
			mask = valconv[2]
			if mask != 0xFF:
				self.read_modify_write(reg, val, mask)
			else:
				self.write(reg, val)
			ln = data.readline()
		del ln
		gc.collect()
	
	# Mask here are the bits we WANT to change
	def read_modify_write(self, addr, val, mask):
		oldval = self.read(addr)
		# mask off oldval. the xor here inverts the mask bits
		oldval &= mask ^ 0xFF
		# make sure we don't write bullshit
		val = val & mask
		val |= oldval
		self.write(addr, val)
	
	def read(self, addr):
		# Check which page we're on, and switch to it if needed.
		regpage = addr & 0x100
		regno = addr & 0xFF
		if self.page != regpage:
			self.setPage(regpage)			
		while not self.dev.try_lock():
			pass		
		# set the register...
		self.dev.writeto(self.addr, bytes([regno]), stop=False)
		result = bytearray(1)
		# and then read from it
		self.dev.readfrom_into(self.addr, result)
		self.dev.unlock()
		return result[0]
	
	def setPage(self, newpage):
		# The page register is always 0xFF.
		# We store the page as just the top bits of the register
		# (i.e. 0, 256, 512, etc.) but then we obviously have to
		# write it shifted down by 8
		while not self.dev.try_lock():
			pass
		val = newpage >> 8
		self.dev.writeto(self.addr, bytes([0xFF, val]), stop=True)
		self.dev.unlock()
		self.page = newpage
	
	# keeping the masks in firmware is *way* too hard,
	# so we just allow any writes. YOU figure it out.
	def write(self, addr, data):
		# check which page we're on and switch to it if needed
		regpage = addr & 0x100
		regno = addr & 0xFF
		if self.page != regpage:
			self.setPage(regpage)
		while not self.dev.try_lock():
			pass
		self.dev.writeto(self.addr, bytes([regno, data]), stop=True)
		self.dev.unlock()					
		
		
		
		
import cobs
from time import sleep

class RadFPGA:
	def __init__(self, uart):
		self.dev = uart
		self.dev.baudrate = 1000000

	def spi_cs(self, device, state):
		self.write(36, state)
	
	def read(self, addr):
		tx = bytearray(4)
		tx[0] = (addr & 0x3F0000)>>16
		tx[1] = (addr & 0xFF00)>>8
		tx[2] = addr & 0xFF
		tx[3] = 3
		self.dev.write(cobs.encode(tx))
		del tx		
		self.dev.write(b'\x00')
		# expect 7 bytes back + 1 overhead + 1 framing
		rx = self.dev.read(9)
		pk = cobs.decode(rx[:8])
		val = pk[3]
		val |= (pk[4] << 8)
		val |= (pk[5] << 16)
		val |= (pk[6] << 24)
		del rx
		del pk
		return val
	
	def writefile(self, fn):
		f = open(fn)
		for line in f.readlines():
			if line[0] == '#':
				continue
			sl = line.split(',')
			reg = int(sl[0])
			val = int(sl[1])
			self.write(reg, val)
				
	def write(self, addr, val):
		tx = bytearray(7)
		tx[0] = (addr & 0x3F0000)>>16
		tx[0] |= 0x80
		tx[1] = (addr & 0xFF00)>>8
		tx[2] = addr & 0xFF
		tx[3] = val & 0xFF
		tx[4] = (val & 0xFF00)>>8
		tx[5] = (val & 0xFF0000)>>16
		tx[6] = (val & 0xFF000000)>>24
		self.dev.write(cobs.encode(tx))
		del tx
		self.dev.write(b'\x00')
		# expect 4 bytes back + 1 overhead + 1 framing
		rx = self.dev.read(6)
		pk = cobs.decode(rx[:5])
		val = pk[3]
		del rx
		del pk
		return val
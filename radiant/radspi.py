# cutdown version of SPI module.

class RadSPI:
	def __init__(self, dev, base, device):
		self.dev = dev
		self.base = base
		self.device = device
		val = self.dev.read(self.base)
		val &= 0xFFFFFFB3
		val |= 0x40
		self.dev.write(self.base, val)
	
	def command(self, command, db, rb, di=[]):
		self.dev.spi_cs(self.device, 1)
		self.dev.write(self.base+0x8, command)
		x = 0
		for d in di:
			self.dev.write(self.base+0x8, d)
			val = self.dev.read(self.base+0x4)
			x += 1
			if val & 0x4:
				return x
		for i in range(db):
			self.dev.write(self.base+0x8, 0)
		val = self.dev.read(self.base+0x4)
		while not val & 0x1:
			self.dev.read(self.base+0x8)
			val = self.dev.read(self.base+0x4)
		rdata = []
		for i in range(rb):
			self.dev.write(self.base+0x8, 0)
			rdata.append(self.dev.read(self.base+0x8))
		self.dev.spi_cs(self.device, 0)
		return rdata
		
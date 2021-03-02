from time import sleep
from micropython import const

class RadCPLD:
	def __init__(self, dev, addr):
		self.dev = dev
		self.addr = addr
		self.tlr = const(0x44001F00)
		self.rti = const(0x45001F00)
		# rti->sir, PLUS sir->sdr
		self.sir = const(0x43000300)
		self.sirrti = const(0x41000100)
		self.sdr = const(0x42000100)
		self.se8 = const(0x47008000)
		self.s8 = const(0x47000000)
		
	def runtest(self, wt):
		self.dev.write(self.addr, 0x41000000)
		sleep(wt)

	def read8(self):
		rv = self.dev.read(self.addr)
		rv >>= 16
		rv &= 0xFF
		return rv	

	def readdr32(self):
		val = 0
		for i in range(4):
			self.dev.write(self.addr, self.s8)
			rv = self.read8()
			rv <<= i*8
			val |= rv
		del rv
		del i
		return val

	def shiftir(self, instr, dorti=True):
		if dorti:
			self.dev.write(self.addr, self.rti)
		self.dev.write(self.addr, self.sir)
		self.dev.write(self.addr, self.se8 | instr)		
	
	def shiftirdr(self, ir, dr, dorti=True):
		self.shiftir(ir, dorti)
		self.dev.write(self.addr, self.sir)
		self.dev.write(self.addr, self.se8 | dr)
		self.dev.write(self.addr, self.sirrti)
		self.runtest(0.001)
			
	def id(self):
		self.shiftir(0xE0)		
		self.dev.write(self.addr, self.sir)
		val = self.readdr32()
		self.dev.write(self.addr, self.tlr)
		return val
		
	def read_status(self):
		self.shiftir(0x3C)
		self.dev.write(self.addr, self.sirrti)		
		self.runtest(0.001)
		self.dev.write(self.addr, self.sdr)
		val = self.readdr32()
		self.dev.write(self.addr,self.tlr)
		return val
	
	def isc_disable(self, dorti=True):
		self.shiftir(0x26, dorti)
		self.dev.write(self.addr, self.sirrti)
		self.runtest(1)
		self.shiftir(0xFF, False)
		self.dev.write(self.addr, self.sirrti)
		for i in range(50):
			self.runtest(0.002)
		self.dev.write(self.addr, self.tlr)		

	def read_feabits(self):
		# need to enable first
		self.shiftirdr(0x74, 0x08)
		# READ_FEABITS
		self.shiftir(0xFB, False)
		self.dev.write(self.addr, self.sir)
		val = self.readdr32()
		val &= 0xFFFF
		self.dev.write(self.addr, self.sirrti)
		# ISC_DISABLE
		self.isc_disable(False)
		return val

	def configure(self, fn):
		f = self.getbitstream(fn)
		if f is None:
			print("File not OK")
			return False
			
		# ISC_ENABLE
		self.shiftirdr(0xC6, 0x00)
		# ISC_ERASE
		self.shiftirdr(0x0E, 0x01, False)
		self.runtest(1)
		# BYPASS
		self.shiftir(0xFF, False)
		rv = self.read8()
		print(hex(rv))
		self.dev.write(self.addr, self.sirrti)		
		# LSC_INIT_ADDRESS
		self.shiftirdr(0x46, 0x1, False)
		# LSC_BITSTREAM_BURST
		self.shiftir(0x7A, False)
		self.dev.write(self.addr, self.sir)
		for i in range(388):
			self.dev.write(self.addr, 0x670000FF)
		val = f.read(1)
		nv = f.read(1)
		while len(nv) > 0:
			self.dev.write(self.addr, 0x67000000 | ord(val))
			val = nv
			nv = f.read(1)
		self.dev.write(self.addr, 0x67008000 | ord(val))
		self.dev.write(self.addr, self.sirrti)
		for i in range(50):
			self.runtest(0.002)				
		self.isc_disable(False)
		f.close()
		
	def getbitstream(self, fn):
		def readstr(f):
			b = bytearray()			
			b.extend(f.read(1))
			while b[-1] != 0:
				b.extend(f.read(1))
			s = str(b,"utf-8")
			del b
			return s
		f = open(fn, "rb")
		val = f.read(2)
		if val != b'\xff\x00':
			return None
		for i in range(13):
			s = readstr(f)
			print(s)
			del s
		del i
		val = f.read(1)
		if val != b'\xff':
			return None
		del val
		return f
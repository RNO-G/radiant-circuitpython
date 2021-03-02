from analogio import AnalogIn
import board
import time

nc = 0.0503

class RadBIST:
	def __init__(self, gpio, dev):
		self.gp = gpio
		self.dev = dev
		
	def labstat(self, lab):
		print("PED:", self.labbist(lab, 2)*nc)
		print("RAMP:", self.labbist(lab, 3)*nc)
		print("AMON:", self.labbist(lab, 5)*nc)
		print("3.0:", self.labbist(lab, 6)*2*nc)
		print("2.5:", self.labbist(lab, 7)*2*nc)		

	def labbist(self, lab, channel):
		towrite = 0x180 | (lab % 12) | (channel << 4)
		if lab < 12:
			self.dev.write(0x8, towrite)
		else:
			towrite = towrite << 16
			self.dev.write(0x8, towrite)
		val = self.bistmon(int(lab/4))
		towrite = 0x1000100
		self.dev.write(0x8, towrite)
		return val
	
	def bistmon(self, quadno, monsig=False):
		min = 0 if quadno < 4 else 3
		max = 3 if quadno < 4 else 6
		for i in range(min, max):
			self.gp.bist(i, True)
			if quadno == i:
				self.gp.quad[i].get_pin(1).value = 1
				self.gp.quad[i].get_pin(3).value = monsig
			else:
				self.gp.quad[i].get_pin(1).value = 0
				self.gp.quad[i].get_pin(3).value = 0
		time.sleep(0.2)
		if quadno < 4:
			p = AnalogIn(board.LQ)
		else:
			p = AnalogIn(board.RQ)
		val = p.value
		self.gp.quad[quadno].get_pin(1).value = 0
		self.gp.quad[quadno].get_pin(3).value = 0
		for i in range(min, max):
			self.gp.bist(i, False)
		p.deinit()
		del p
		del i
		del min
		del max		
		return val				
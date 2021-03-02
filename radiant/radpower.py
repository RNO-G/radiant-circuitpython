from time import sleep
from radbase import RadPowerCore
from digitalio import DigitalInOut, Pull
from analogio import AnalogIn
import board

class RadPowerRail:
	def __init__(self, pgpin, analogpin=None):
		self.pg = DigitalInOut(pgpin)
		self.pg.switch_to_input(pull=Pull.UP)
		if analogpin:
			self.mon = AnalogIn(analogpin)
		else:
			self.mon = None

class RadPower:
	def __init__(self):
		self.core = RadPowerCore()		
		self.INT = RadPowerRail(board.PGV10, board.V10)
		self.AUX = RadPowerRail(board.PGV18, board.V18)
		self.IO = RadPowerRail(board.PGV25, board.V25)
		self.LAB = RadPowerRail(board.PGV26)
		self.TRIG = RadPowerRail(board.PGV31)

	def fpga(self, mode):
		if mode:
			self.core.v10 = True
			sleep(0.01)
			self.core.v18 = True
			sleep(0.01)
			self.core.v25 = True
			sleep(0.01)
		else:
			self.core.v25 = False
			self.core.v18 = False
			self.core.v10 = False
	
	def trig(self, mode):
		if mode:
			self.core.v31 = True
			sleep(0.01)
			if self.TRIG.pg.value is not True:
				print("TRIG power good did not become True!")
				return False
			return True
		else:
			self.core.v31 = False
			return False
	
	def lab(self, mode):
		if mode:
			self.core.v26 = True
			sleep(0.01)
			if self.LAB.pg.value is not True:
				print("LAB power good did not become True!")
				return False
			return True
		else:
			self.core.v26 = False
			return False
	
	def all(self, mode):
		self.fpga(mode)
		self.trig(mode)
		self.lab(mode)

	def status(self):
		self.railStatus("1.0  ", self.INT, self.core.v10)
		self.railStatus("1.8  ", self.AUX, self.core.v18)
		self.railStatus("2.5  ", self.IO, self.core.v25)
		self.railStatus("A2.5 ", self.LAB, self.core.v26)
		self.railStatus("A3.0 ", self.TRIG, self.core.v31)

	def railStatus(self, name, rail, enpin):
		print(name, 3.3*rail.mon.value/65536. if rail.mon else " ", "ON " if enpin else "OFF ", "GOOD" if rail.pg.value else "BAD")
		
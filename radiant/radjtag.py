from time import sleep
import board
from digitalio import DigitalInOut, Direction

# RadJTAG is a MASSIVELY compacted JTAG
# loader. JTAG loading always works
# exactly the goddamn same for every Xilinx
# FPGA: you clock the thing to CTL0 and
# just go wacko clocking inthe bistream.
#
# Yes, this is slow right now. Big whoop.
class RadJTAG:
	def __init__(self, fn="radboot.bin"):
		self.fn = fn
		self.tck = DigitalInOut(board.TCK)
		self.tms = DigitalInOut(board.TMS)
		self.tdi = DigitalInOut(board.TDI)
		self.tdo = DigitalInOut(board.TDO)
		self.tck.switch_to_output(value=False)
		self.tms.switch_to_output(value=False)
		self.tdi.switch_to_output(value=False)
		self.tdo.switch_to_input()
	
	def clock(self, tdi=False):
		self.tdi.value = tdi
		self.tck.value = True
		self.tck.value = False
	
	def idcode(self):
		self.tms.value = True
		self.clock()
		# select-DR
		self.tms.value = False
		self.clock()
		# capture-DR
		self.clock()
		# now in shift-DR.
		# Data appears on TDO *now*
		# data is clocked into TDI *at next clock*
		val = 0		
		for i in range(32):
			val |= int(self.tdo.value) << i
			# could exit at 32 here if I felt like it
			self.clock()
		self.tms.value = True
		self.clock()
		self.clock()
		self.tms.value = False
		self.clock()
		return val
	
	def shiftir(self, value):
		# assume we start in RTI
		self.tms.value = True
		self.clock()
		# Select-DR
		self.clock()
		# Select-IR
		self.tms.value = False
		self.clock()
		# capture-ir		
		self.clock()
		# shift-ir
		for i in range(5):
			self.clock(value & 0x1)
			value = value >> 1
		self.tms.value = True
		self.clock(value & 0x1)
		# exit1-IR : now go to RTI
		self.clock()
		# update-IR
		self.tms.value = False
		self.clock()
		# RTI
		
	def begin(self):
		# TLR
		self.tms.value = True
		self.tdi.value = True
		for i in range(5):
			self.clock()
		# go to RTI
		self.tms.value = False
		self.tdi.value = False
		self.clock()
	
	def config(self):
		# Config sequence is simple, just:
		# JPROGRAM
		self.shiftir(0x0b)
		# NOOP
		self.shiftir(0x14)
		# wait at least 0.1 sec
		time.sleep(0.1)
		# Can shift in 0x14 and look
		# at the IR output. As far as I can
		# tell, Xilinx just checks
		# DONE=0 and INIT=1.
		# now shift in CONFIG
		self.shiftir(0x05)
		# and GO CRAZY shifting in the
		# bitstream in BIT REVERSED ORDER
		# e.g. in the XSVF the sync word looks like 66aa9955
		# 0110 0110 1010 1010 1001 1001 0101 0101
		# whereas it's actually aa995566
		# 1010 1010 1001 1001 0101 0101 0110 0110
		# then it's just
		# JSTART (0x0C)
		# go to RTI and clock in 100 times
		# then it goes and checks again, but who cares
		
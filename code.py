from radiant.radpower import RadPower
from radiant.radclock import RadClock
import board

VCC = RadPower()
if VCC.core.poweron:
	# This only happens our first loop through.
	VCC.fpga(True)
	i2c = board.I2C()
	ck = RadClock(i2c)
	ck.configure("intclock25.dat")
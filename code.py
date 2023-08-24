from radiant.radpower import RadPower
from radiant.radclock import RadClock
import board

VCC = RadPower()
if VCC.core.poweron:
	# This only happens our first loop through.
	VCC.fpga(True)
	i2c = board.I2C()
	ck = RadClock(i2c)
	if(ck.clock_rate==3200): ck.configure("intclock25.dat")
	else: ck.configure("intclock18_75.dat")

def getval(mon):
	val = mon.value - 3800
	return val*3.3/65536

def labmonset(dev, lab, val):
	towrite = 0x180 | (val << 4) | lab;
	dev.write(0x8, towrite)

def amonset(dev, lab, val):
	towrite = 0x8000c000
	towrite |= (lab << 24)
	towrite |= val
	dev.write(0x10018, towrite)
	
def dumpAnalogMon(dev, mon):
	labmonset(dev, 0, 7)
	print(" A2.5V0:", getval(mon))
	labmonset(dev, 0, 6)
	print(" T03.0V:", getval(mon))
	labmonset(dev, 0, 2)
	print("    VP0:", getval(mon))
	labmonset(dev, 0, 5)
	amonset(dev, 0, 0)
	print("    VBS:", getval(mon))
	amonset(dev, 0, 1)
	print("  VBIAS:", getval(mon))
	amonset(dev, 0, 2)
	print(" VBIAS2:", getval(mon))
	amonset(dev, 0, 3)
	print("CMPBIAS:", getval(mon))
	amonset(dev, 0, 4)
	print("  VADJP:", getval(mon))
	amonset(dev, 0, 5)
	print("  QBIAS:", getval(mon))
	amonset(dev, 0, 6)
	print("   ISEL:", getval(mon))
	amonset(dev, 0, 7)
	print(" VTRIMT:", getval(mon))
	amonset(dev, 0, 8)
	print("  VADJN:", getval(mon))
		
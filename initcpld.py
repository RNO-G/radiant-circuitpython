# program the FEABITS for the CPLD to allow it to work
def initcpld(pld):
	pld.dev.write(0x14, 0x80000000)
	pld.shiftirdr(0xC6, 0x08)
	pld.shiftirdr(0x0E, 0x02, False)
	pld.runtest(1)
	pld.shiftirdr(0x46, 0x02, False)
	pld.shiftir(0xE4, False)
	pld.dev.write(pld.addr, pld.sir)
	for i in range(7):
		pld.dev.write(pld.addr, pld.s8)
	pld.dev.write(pld.addr, pld.se8)
	pld.dev.write(pld.addr, pld.sir)
	pld.runtest(0.001)
	checkbusy(pld)
	pld.shiftir(0xF8, False)
	pld.dev.write(pld.addr, pld.sir)
	pld.dev.write(pld.addr, 0x47000020)
	pld.dev.write(pld.addr, 0x47008007)
	pld.dev.write(pld.addr, pld.sirrti)	
	pld.runtest(0.001)
	checkbusy(pld)	
	pld.isc_disable(False)
	
def checkbusy(pld):
	pld.shiftir(0xF0, False)
	val = 1
	lc = 0
	while val & 0x1:		
		pld.dev.write(pld.addr, pld.sirrti)
		pld.runtest(0.001)
		pld.dev.write(pld.addr, pld.sdr)
		pld.dev.write(pld.addr, 0x40000100)
		val = pld.read8()
		lc = lc + 1
		if lc > 10:
			break
	if lc > 10:
		print("BUSY never went low!")
	pld.dev.write(pld.addr, pld.sirrti)
	
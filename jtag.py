import digitalio
import board
import binascii
import gc

class JTAG:
	def __init__(self):
		self.tck = digitalio.DigitalInOut(board.TCK)
		self.tdi = digitalio.DigitalInOut(board.TDI)
		self.tms = digitalio.DigitalInOut(board.TMS)
		self.tdo = digitalio.DigitalInOut(board.TDO)
	
	def open(self):
		self.tck.switch_to_output(value=False)
		self.tms.switch_to_output(value=False)
		self.tdi.switch_to_output(value=False)
		self.tdo.switch_to_input(pull=digitalio.Pull.UP)
	
	def close(self):
		self.tck.switch_to_input()
		self.tms.switch_to_input()
		self.tdi.switch_to_input()
	
	def clock(self, tmsval, tdival):
		# is this right? no idea...
		tdobit = self.tdo.value
		self.tms.value = tmsval
		self.tdi.value = tdival
		self.tck.value = True
		self.tck.value = False
		return tdobit
	
	def tlr(self):
		for i in range(5):
			self.clock(1, 1)
	
	def enumerate(self):
		self.tlr()
		
		self.clock(0, 1)
		self.clock(1, 1)
		self.clock(0, 1)
		idcode = 0
		for i in range(32):
			idcode >>= 1
			tdobit = self.clock(0, 1)
			if tdobit:
				idcode |= 0x80000000
		self.tlr()
		return idcode
	
	def xvcd(self):
		self.open()
		self.tlr()
		exit = False		
		while not exit:
			cmd = input()
			if cmd == "exit:":
				exit = True
			else:
				decode = binascii.a2b_base64(cmd)
				xvcmd = decode[:decode.find(b':')]
				xvarg = decode[len(xvcmd)+1:]
				if xvcmd == b'exit':
					exit = True
				else:
					resp = self.xvcProcess(xvcmd, xvarg)
					print(binascii.b2a_base64(resp).decode('utf-8'), end='')
			gc.collect()
						
	def xvcProcess(self, cmd, arg):
		if cmd == b'getinfo':
			resp = b'xvcServer_v1.0:64\n'
		elif cmd == b'settck':				
			resp = bytearray(4)
			resp[0] = 0
			resp[1] = 4
			resp[2] = 0
			resp[3] = 0
		elif cmd == b'shift':
			nbits = arg[0]
			nbits += arg[1] << 8
			nbits += arg[2] << 16
			nbits += arg[3] << 24
			nbytes = (nbits+7)>>3
			resp = bytearray(nbytes)
			for i in range(nbytes):
				if nbits < 8:
					bitlen = nbits
				else:
					bitlen = 8
				tmsval = arg[4+i]
				tdival = arg[4+nbytes+i]
				resp[i] = 0
				for j in range(8):
					resp[i] >>= 1
					if j < bitlen:
						tdobit = self.clock(tmsval & 0x1, tdival & 0x1)
					else:
						tdobit = 0
					if tdobit:
						resp[i] |= 0x80
					tmsval >>= 1
					tdival >>= 1
				nbits -= bitlen
					
		return resp
						

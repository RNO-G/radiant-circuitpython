# The MIT License (MIT)
#
# Copyright (c) 2017 Tony DiCola for Adafruit Industries
#                    refactor by Carter Nelson
#                    reredone by Patrick Allison for XRA1200 (and identicals)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`xra1200`
====================================================

CircuitPython module for the XRA1200 I2C I/O extenders.

* Author(s): Tony DiCola
"""

from micropython import const
from .mcp230xx import MCP230XX
from .digital_inout import DigitalInOut

# pylint: disable=bad-whitespace
_XRA1200_ADDRESS = const(0x20)
_XRA1200_GSR = const(0x00)
_XRA1200_OCR = const(0x01)
_XRA1200_PIR = const(0x02)
_XRA1200_GCR = const(0x03)
_XRA1200_PUR = const(0x04)
_XRA1200_IER = const(0x05)
_XRA1200_TSCR = const(0x06)
_XRA1200_ISR = const(0x07)
_XRA1200_REIR = const(0x08)
_XRA1200_FEIR = const(0x09)
_XRA1200_IFR = const(0x0A)

class XRA1200(MCP230XX):
	def __init__(self, i2c, address=_XRA1200_ADDRESS, defaultdir=0xFF, defaultio=None):
		super().__init__(i2c, address)

		self.iodir = defaultdir
		#self.gppu = 0x00
		if defaultio is not None:
			self.gpio = defaultio
		self._write_u8(_XRA1200_PIR, 0x00)

	@property
	def gpio(self):
		return self._read_u8(_XRA1200_GSR)

	@gpio.setter
	def gpio(self, val):
		self._write_u8(_XRA1200_OCR, val)

	@property
	def iodir(self):
		return self._read_u8(_XRA1200_GCR)

	@iodir.setter
	def iodir(self, val):
		self._write_u8(_XRA1200_GCR, val)

	@property
	def gppu(self):
		return self._read_u8(_XRA1200_PUR)

	@gppu.setter
	def gppu(self, val):
		self._write_u8(_XRA1200_PUR, val)

	def get_pin(self, pin):
		assert 0 <= pin <= 7
		return DigitalInOut(pin, self)
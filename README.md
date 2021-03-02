# RADIANT CircuitPython core

This Python code is for running **on** the Board Manager in CircuitPython
mode. At some point portions of this + the full radiant-python core need
to be merged, because in a lot of ways they're dead copies of each other.

But because this is the CircuitPython core, there's not a ton of comments
and a fair amount of magic numbers. See the radiant-python code for
more details.

Again: see https://github.com/rno-g/radiant-python

# Why CircuitPython

Because it allowed me to develop stuff **really** fast. Nominally it could
also be used to let the RADIANT run completely standalone as well, but
that's a future pipe dream.

However I do end up using the extra SPI flash (they're **a dollar**), and
the easiest way to write the SPI flash is to just load the CircuitPython
instance which allows it to just pop up on a computer as a USB drive.

# Important note

The "intclock25.dat" and "radiant-spiflash.bit" files **must** be loaded
on the CIRCUITPY drive. They're used by the Arduino code to load the
clock and put the FPGA in rescue mode.

The other files are helpful for initial checkout but depending on how we
end up doing things might not be necessary at all.
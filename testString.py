import argparse
import logging
import pprint
import time
import os
import sys
import struct
def main():
	x = 25200
	y = hex(x).split('x')[1]
	if x < 16:
		data = '\\' + "x00" + '\\' + "x0" + hex(x).split('x')[1]	
	elif x >= 16 and x < 256:
		data = '\\' + "x00" + '\\' + "x" + hex(x).split('x')[1]
	elif x >= 256 and x < 4096:
		data = '\\' + "x0" + y[0] + '\\' + "x" + y[1:]
	elif x >= 4096:
		data = '\\' + "x" + y[0:2] + '\\' + "x" + y[2:]
	z = struct.pack('>I', 4314)
	print (z)
	#y = hex(x).split('x')[1]
	#y = [y[start:start+2] for start in range(0, len(y), 2)]
	#z = '\xFF\xAA'
	#z.sub('FF', y[0] )
	#print(z)
	#z.replace('AA', y[1])
	#print(z)


def split(str, num):
    return [ str[start:start+num] for start in range(0, len(str), num) ]
    
    
if __name__ == '__main__':
    main()

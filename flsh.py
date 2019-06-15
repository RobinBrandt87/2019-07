   1 #!/usr/bin/env python3
   2 
   3 import argparse
   4 
   5 from ftplib import FTP
   6 from sys import argv
   7 from os import stat
   8 
   9 parser = argparse.ArgumentParser(description='Tool to boot AVM EVA ramdisk images.')
  10 parser.add_argument('ip', type=str, help='IP-address to transfer the image to')
  11 parser.add_argument('image', type=str, help='Location of the ramdisk image')
  12 parser.add_argument('--offset', type=lambda x: int(x,0), help='Offset to load the image to in hex format with leading 0x. Only needed for non-lantiq devices.')
  13 args = parser.parse_args()
  14 
  15 size = stat(args.image).st_size
  16 # arbitrary size limit, to prevent the address calculations from overflows etc.
  17 assert size < 0x2000000
  18 
  19 if args.offset:
  20         addr = size
  21         haddr = args.offset
  22 else:
  23         # We need to align the address.
  24         # A page boundary seems to be sufficient on 7362sl and 7412
  25         addr = ((0x8000000 - size) & ~0xfff)
  26         haddr = 0x80000000 + addr
  27 
  28 img = open(args.image, "rb")
  29 ftp = FTP(args.ip, 'adam2', 'adam2')
  30 
  31 def adam(cmd):
  32         print("> %s"%(cmd))
  33         resp = ftp.sendcmd(cmd)
  34         print("< %s"%(resp))
  35         assert resp[0:3] == "200"
  36 
  37 ftp.set_pasv(True)
  38 # The following parameters allow booting the avm recovery system with this
  39 # script.
  40 adam('SETENV memsize 0x%08x'%(addr))
  41 adam('SETENV kernel_args_tmp mtdram1=0x%08x,0x88000000'%(haddr))
  42 adam('MEDIA SDRAM')
  43 ftp.storbinary('STOR 0x%08x 0x88000000'%(haddr), img)
  44 img.close()
  45 ftp.close()

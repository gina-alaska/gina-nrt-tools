#!/usr/bin/env /awips2/python/bin/python
#####################################################################
#
# ncImageQC.py - script for scanning a regionalsat netcdf image file
# for valid (non-zero) pixels and image contrast. If command line 
# input thresholds are not met the script will return "FAIL" 
# Arguments: -c #####   defines a minimum number of valid pixels in
#                       order for the image to pass
#            -r #####   defines the range of pixel values that would
#                       be considered valid for an image to pass
#
#####################################################################
import os, sys
import numpy
import argparse
import Scientific.IO.NetCDF
from Scientific.IO import NetCDF

#####################################################################

def _process_command_line():
    """Process the command line arguments.

    Return an argparse.parse_args namespace object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--mincnt', type=int, default=0, action='store', help='min num valid pixels'
    )
    parser.add_argument(
        '-r', '--minrng', type=int, default=0, action='store', help='min range of pixels'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='verbose flag'
    )
    parser.add_argument(
        'filepath', help='netCDF file path'
    )
    args = parser.parse_args()
    return args

#####################################################################

def qc_image_file(filepath, mincnt, minrng):
   """Process the command line arguments."""

   if not os.path.exists(filepath):
      print "File not found: ", filepath 
      raise SystemExit
   try:
      cdf_fh = NetCDF.NetCDFFile(filepath, "r")
   except IOError:
      print 'Error opening {}'.format(filepath)
      raise SystemExit
   except OSError:
      print 'Error accessing {}'.format(filepath)
      raise SystemExit

   varid = cdf_fh.variables['image']
   pixdata = varid.getValue()
   cdf_fh.close()
   #
   pixcnt = numpy.sum(pixdata != 0)
   if pixcnt > 0:
      pixmax = numpy.max(pixdata)
      pixmin = numpy.min(pixdata[numpy.nonzero(pixdata)])
      pixrng = int(pixmax) - int(pixmin)
      
   #
   if verbose:
      print "pixmax = {} pixmin = {}".format(pixmax, pixmin)
      print "{} pixels with range: {}".format(pixcnt, pixrng)

   if mincnt == 0 and minrng == 0:
      return True
   #
   if mincnt > 0 and pixcnt < mincnt:
      if verbose:
         print "Too few valid pixels"
      return False
   elif minrng > 0 and pixrng < minrng:
      if verbose:
         print "Range too narrow"
      return False
   else:
      return True

   return

#####################################################################

def main():
   """ counts valid pixels in satellite netcdf file."""
   global verbose
   #
   pixmax = 0
   pixmin = 0
   pixrng = 0
   # process command line arguements
   args = _process_command_line()

   verbose = args.verbose
   if args.mincnt == 0 and args.minrng == 0:
      if verbose == False:
         print "No thresholds specified...reporting results only:"
         verbose = True
   #
   if qc_image_file(args.filepath, args.mincnt, args.minrng) == False:
      print "QC FAIL"
   else:
      if args.mincnt > 0 and args.minrng > 0:
         print "QC PASS"

   return

if __name__ == '__main__':
    # This is only executed if the script is run from the command line.
    main()

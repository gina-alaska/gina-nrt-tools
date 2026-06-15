#!/usr/bin/env /usr/bin/python3

import urllib.request
import datetime
import os, sys
import gzip
from shutil import copy, move, copyfileobj
import argparse
from time import strftime
from datetime import datetime, timedelta

##################

def _process_command_line():
    """Process the command line arguments.

    Return an argparse.parse_args namespace object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'sensor', nargs='+', choices=['viirs','modis','metop','avhrr','atms','amsr2','all'],
        help='satellite sensors to download'
    )
    parser.add_argument(
        '-a', '--antenna', action='store', default='all', choices=['uaf5','gilmore','uafgina'],
	help='antenna source')
    parser.add_argument(
        '-s', '--satellite', action='store', default='all', choices=['terra','snpp',
	'noaa21','noaa20','metop-c','metop-b','gcom-w','aws'],help='satellite source')
    parser.add_argument(
        '-m', '--match', action='store', default='', help='match substring in filename')
    parser.add_argument(
        '-l', '--level', action='store', default='scmi', choices=['level1','level2','scmi',
	'mirs_awips','mirs_scmi','sst_awips','nucaps_level2','clavrx_scmi','mirs_level2',
        'awips','NucapsAwips','edr_scmi','sst_geotif','raw','nucaps_level1','mod14', 
        'mirs_level2','mirs_geotif_l1','mirs_awips','level1_agg','level0-ipopp', 
        'geotiff_polar_l2','geotiff_polar_l1','geotiff_ngfs_l2','geotiff_level2', 
        'geotiff_l2','geotiff_l1','geotiff_gm_l2','geotiff_gm_l1','geotiff', 
        'FireAwips','fire','edr_geotiff_l1','clavrx_level2','clavrx_geotiff_l1',
	'binary_slice','acspo_level2,','acspo_awips'], help='data processing level')
    parser.add_argument(
        '-t', '--test', action='store_true', help='use test NRT data stream')
    parser.add_argument(
        '-ni', '--noingest', action='store_true', help='no AWIPS ingest, transfer file only')
    parser.add_argument(
        '-reg', '--regionalsat', action='store_true', help='add the prefix Alaska to regionalsat filenames that AWIPS needs needs for identification')
    parser.add_argument(
        '-bm', '--backmins', type=int, action='store', default=61,
        help='num mins back to consider')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='verbose flag'
    )
    parser.add_argument(
        '-ver', '--version', action='version', version="%(prog)s 2.0.0", help='version value'
    )
    args = parser.parse_args()
    return args

######################################################


def build_url(datasrc, antenna, satellite, sensor, level, bgnstr, endstr):
    """Build the GINA product list URL based on antenna, satellite, and sensor filters.
    
    Args:
        datasrc   : data source string (e.g. 'nrt-prod' or 'nrt-test')
        antenna   : antenna/facility name or 'all'
        satellite : satellite name or 'all'
        sensor    : sensor name or 'all'
        level     : processing level string
        bgnstr    : begin datetime string (YYYY-MM-DD+HHMM)
        endstr    : end datetime string (YYYY-MM-DD+HHMM)

    Returns:
        str: fully constructed URL
    """
    base = f"http://{datasrc}.gina.alaska.edu/products.txt?"
    params = {
        "processing_levels[]": level,
        "start_date": bgnstr,
        "end_date": endstr,
    }

    if antenna != "all":
        params["facilities[]"] = antenna
    if satellite != "all":
        params["satellites[]"] = satellite
    if sensor != "all":
        params["sensors[]"] = sensor

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return base + query_string


######################################################

def main(): 

   global sensor, verbose, testsrc
   ##++++++++++++++++  Configuration section +++++++++++++++++++++++## 
   ingestDir = "/data_store/dropbox"
   downloadDir = "/data_store/download"
   minPixelCount = 60000    # minimum number of pixels for image to be valid
   minPixelRange = 50       # minimum range of pixel values for valid image
   ##++++++++++++++++++  end configuration  ++++++++++++++++++++++++## 
   #
   ###### definitions base on command line input
   args = _process_command_line()
   verbose = args.verbose      # turns on verbose output
   antenna = args.antenna      # specifies single satellite platform
   satellite = args.satellite  # specifies single satellite platform
   testsrc = args.test         # directs data requests to test NRT stream
   matchstr = args.match       # directs data requests to test NRT stream
   if args.noingest:
      doingest = 0
   else:
      doingest = 1
   #
   if testsrc:
       datasrc = "nrt-test"
   else:
       datasrc = "nrt-prod"
   level = args.level
   #
        
   bgntime = datetime.utcnow() - timedelta(minutes=args.backmins)
   endtime = datetime.utcnow()
   bgnsecs = bgntime.strftime("%s")
   bgnstr = bgntime.strftime("%Y-%m-%d+%H%M")
   endstr = endtime.strftime("%Y-%m-%d+%H%M")
   #print (f"level={level}  satellite={satellite}")
   ######
   dset_count = {"modis":0,"viirs":0,"avhrr":0,"metop":0,"atms":0,"amsr2":0,"all":0}
   #
   if verbose:
      print (f"Dates: {bgnstr} / {endstr}")
   #
   downloads = 0
   for sensor in args.sensor:
      print (f"Requesting: {sensor}")
      #
      listurl = build_url(datasrc, antenna, satellite, sensor, level, bgnstr, endstr)
      #
      print (f"URL={listurl}")
      sock = urllib.request.urlopen (listurl)

      htmlSource = str(sock.read(),'UTF-8')
      sock.close()
      if verbose:
         print ("BEGIN HTML =======================================================")
         print (htmlSource)
         print ("END HTML =========================================================")
      print(f"Response length = {len(htmlSource)}")
      #
      # Parse the response into a list of non-empty filenames
      satfile = [line.strip() for line in htmlSource.splitlines() if line.strip()]
      # change working location to the download scratch directory
      if doingest:
         os.chdir(downloadDir)
      # now parse the file name and retrieve the recent files 
      dcount = 0
      ingcount = 0
      totsize = 0
      for fileurl in satfile:
         # the test location for files is different than the operational location
         if testsrc:
            fileurl = fileurl.replace("dds.gina.alaska.edu/nrt","nrt-dds-test.gina.alaska.edu")
         if verbose:
            print (f"Downloading: {fileurl}")
         filename = f"{fileurl.split('/')[-1]}"
         if matchstr:
            #print (f"looking for matchstr=[{matchstr}]")
            if matchstr in filename:
               print (f"Found: {filename}")
            else:
               continue

         print (f"FILENAME={filename}")
         urllib.request.urlretrieve(fileurl, filename)
         if os.path.isfile(filename):
            fsize = os.path.getsize(filename)
            dcount += 1                      
            nameseg = filename.split('.')
            basenm = nameseg[0]              
            if verbose: 
               print (f"Basename = {basenm}")
            # use base name to create a new name with "Alaska" prefix and ".nc" extension
            if args.regionalsat:
               newfilename=f"Alaska_{basenm}.nc"
               print (f"Adding prefix: {newfilename}")
            else:
               newfilename=filename

            # now look for ".gz" in file name to determine if compression is needed
            if ".gz" in filename:
               # open compressed file and read out all the contents
               inF = gzip.GzipFile(filename, 'rb')
               s = inF.read()
               inF.close()
               # now write uncompressed result to the new filename
               outF = open(newfilename, 'wb')
               outF.write(s)
               outF.close()
               # make sure the decompression was successful
               if not os.path.exists(newfilename):
                   print (f"Decompression failed: {filename}")
                   raise SystemExit
               # redirected compression copies to a new file so old compressed file needs to be removed
               os.remove(filename)
               #
               if verbose:
                  print (f"File decompressed: {newfilename}")

            elif ".nc" in filename:
               move(filename, newfilename)
            #
            # set the filename variable to the new uncompressed name
            filename = newfilename
            ###############################################
            # Now check if the file already exists ingest directory
            ingestfilename = f"{ingestDir}/{filename}"
            if os.path.exists(ingestfilename):
               print (f"File already exists in Ingest Dir...removing: {filename}")
               os.remove(filename)
               continue
            elif doingest:
               # OK, ready to move the file to the ingest directory
               print (f"Moving {filename} to {ingestDir}")
               try:
                  move(filename,ingestDir)
               except:
                  print (f"*******  Unable to  move file to ingest: {filename}")
                  continue
            else:
               print (f"No local ingest for {filename}")
            ingcount += 1
            print (f"INGEST CNT = {ingcount}")
            # 
         else:
            fsize = 0

         totsize += fsize
         downloads += 1
         dset_count[sensor] += 1

   for sensor in args.sensor:
      print (f"{sensor} files downloaded={dset_count[sensor]}")
   print (f"Total files downloaded={downloads} ingested={ingcount}  total size={totsize}")

if __name__ == '__main__':
    main()


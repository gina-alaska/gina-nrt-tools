# Fetching
This directory includes sample scripts for fetching data from GINA's NRT system. 
 - [mirror_products.sh](./mirror_products.sh) provides a template for retrieving data from a unix command line.
 - [fetch_products.py](./fetch_products.py) provides similar functionality in python, with additional filtering options.

See sections below for further details on these two scripts. These scripts should be considered templates and are not intended to have fully developed error handling.

Dropdown options can be viewed at http://nrt-status.gina.alaska.edu/products to determine available parameters. Parameters may change over time with updates, such as the addition of new satellite retrievals.

## mirror_products.sh
- This script is intended to provide an easy way to retrieve data from GINA's NRT processing system in a scripted manner.  It is intended to be used on a modern linux box, but should work on most unix based systems.
- This script is intended to be run on a directory at a fixed interval - it will pull data matching the arguements (see below),  and skip any data that was previously downloaded. 
- It can be used as a starting point for a custom script if it does not meet the users needs. 
- It has these options (from ./mirror_products.sh -h ):
```
OPTIONS:
 -h   Show this message
 -s   Fetch data for SATELLITE
 -i   Fetch data for SENSOR
 -f   Fetch data for FACILITY
 -p   Fetch data for PROCESSING_LEVEL
 -n   Namespace the data (Place in sub-directorys for each pass)
 -o   Path to write data to (Default: .)
```
A few notes on the arguments:
* Satellite (-s)
  * examples: noaa21, metop-c
* Sensor (-i) 
  - examples: viirs, avhrr
* Facility( -f ) 
  - we recommend users __do not__ specify a facility as satellite passes may be recieved at different facilities depending on priorites.
* Processing level (-p) 
  - most users are interested in level1 data (level1) or geotiff data (geotiff_l2). Contact us at support@gina.alaska.edu if other datasets are needed and we can offer advice.
* namespace (-n)
  - this option places each "pass" in it's own directory - this is useful if a pass is taken at two sites, and the different sites will end up in seperate directories.  Without this option the files are all placed inside the path specified in the "-o" option. 


## Examples

* To fetch all the recient GeoTiff data that goes into Feeder, with different "passes" in their own subdirectories:
```
 ./mirror_products.sh  -p geotiff_l2 -n -o ./test/ 
 tree test
test
├── JPSS1.20260609.212259
│   ├── noaa20.20260609.2122_DNB_adaptive.small.png
│   ├── noaa20.20260609.2122_DNB_adaptive.tif
│   ├── noaa20.20260609.2122_DNB.small.png
│   ├── noaa20.20260609.2122_DNB.tif
│   ├── noaa20.20260609.2122_I03_I02_I01.small.png
│   ├── noaa20.20260609.2122_I03_I02_I01.tif
│   ├── noaa20.20260609.2122_i03_m08_i01.small.png
│   ├── noaa20.20260609.2122_i03_m08_i01.tif
│   ├── noaa20.20260609.2122_i04_colored.small.png
│   ├── noaa20.20260609.2122_i04_colored.tif
│   ├── noaa20.20260609.2122_i04_i02_i01.small.png
│   ├── noaa20.20260609.2122_i04_i02_i01.tif
│   ├── noaa20.20260609.2122_i05_colored.small.png
│   ├── noaa20.20260609.2122_i05_colored.tif
│   ├── noaa20.20260609.2122_I05.small.png
│   ├── noaa20.20260609.2122_I05.tif
│   ├── noaa20.20260609.2122_m12_m11_m10.small.png
│   ├── noaa20.20260609.2122_m12_m11_m10.tif
│   ├── noaa20.20260609.2122_micro_physics.small.png
│   ├── noaa20.20260609.2122_micro_physics.tif
│   ├── noaa20.20260609.2122_true_color.small.png
│   └── noaa20.20260609.2122_true_color.tif
├── NPP.20260609.210420
│   ├── npp.20260609.2102_i03_m08_i01.small.png
│   ├── npp.20260609.2102_i03_m08_i01.tif
│   ├── npp.20260609.2102_i04_colored.small.png
│   ├── npp.20260609.2102_i04_colored.tif
│   ├── npp.20260609.2102_i05_colored.small.png
│   ├── npp.20260609.2102_i05_colored.tif
│   ├── npp.20260609.2102_micro_physics.small.png
│   └── npp.20260609.2102_micro_physics.tif
└── tp2026160214355.METOP-C.dat.gz
    ├── metop-c.20260609.2145_3a_2_1.small.png
    ├── metop-c.20260609.2145_3a_2_1.tif
    ├── metop-c.20260609.2145_4.small.png
    ├── metop-c.20260609.2145_4.tif
    ├── metop-c.20260609.2145_5.small.png
    └── metop-c.20260609.2145_5.tif
(snip..)
```
* To fetch all the recient L1 VIIRS data from SNPP:
```
./mirror_products.sh -p level1 -i viirs -s snpp -n -o ./test/
$ tree test
test
├── npp.17240.0952
│   ├── GDNBO_npp_d20170828_t0957524_e0959168_b30234_c20170828100334127887_cspp_dev.h5
│   ├── SVDNB_npp_d20170828_t0957524_e0959168_b30234_c20170828100333861647_cspp_dev.h5
│   ├── SVI02_npp_d20170828_t0955016_e0956257_b30234_c20170828100352756666_cspp_dev.h5
│   ├── SVI02_npp_d20170828_t0956270_e0957511_b30234_c20170828100352763224_cspp_dev.h5
│   ├── SVI03_npp_d20170828_t0953361_e0955003_b30234_c20170828100335872111_cspp_dev.h5
│   ├── SVI04_npp_d20170828_t0953361_e0955003_b30234_c20170828100335879192_cspp_dev.h5
│   ├── SVI04_npp_d20170828_t0956270_e0957511_b30234_c20170828100352774310_cspp_dev.h5
│   ├── SVI05_npp_d20170828_t0953361_e0955003_b30234_c20170828100335963344_cspp_dev.h5
│   ├── SVM01_npp_d20170828_t0956270_e0957511_b30234_c20170828100352944247_cspp_dev.h5
│   ├── SVM03_npp_d20170828_t0955016_e0956257_b30234_c20170828100352968960_cspp_dev.h5
│   ├── SVM05_npp_d20170828_t0957524_e0959168_b30234_c20170828100336249111_cspp_dev.h5
│   ├── SVM08_npp_d20170828_t0955016_e0956257_b30234_c20170828100353024447_cspp_dev.h5
│   ├── SVM11_npp_d20170828_t0955016_e0956257_b30234_c20170828100353109945_cspp_dev.h5
│   ├── SVM12_npp_d20170828_t0956270_e0957511_b30234_c20170828100353064030_cspp_dev.h5
│   ├── SVM14_npp_d20170828_t0953361_e0955003_b30234_c20170828100336251733_cspp_dev.h5
│   ├── SVM14_npp_d20170828_t0956270_e0957511_b30234_c20170828100353193632_cspp_dev.h5
│   ├── SVM14_npp_d20170828_t0957524_e0959168_b30234_c20170828100336426450_cspp_dev.h5
│   └── SVM16_npp_d20170828_t0957524_e0959168_b30234_c20170828100336482948_cspp_dev.h5
└── NPP.20170828.095006.dat.gz
    ├── SVDNB_npp_d20170828_t0953362_e0955003_b30234_c20170828100709175074_cspp_dev.h5
    ├── SVI04_npp_d20170828_t0952108_e0953349_b30234_c20170828100728179485_cspp_dev.h5
    └── SVM14_npp_d20170828_t0952108_e0953349_b30234_c20170828100730671028_cspp_dev.h5
(snip)
```


## fetch_products.py

- This script provides the same data access as mirror_products.sh with similar parameters.

- Additional options exist for filtering by a wildcard and suffix

### Usage

```bash
$ python fetch_products.py  -h
usage: fetch_products.py [-h] [-s SATELLITE] [-i SENSOR] [-f FACILITY] [-p PROCESSING_LEVEL] [-n]
                         [-o OUTPUT] [-z] [--start-date START_DATE] [--end-date END_DATE] [-w WILDCARD]
                         [--suffix SUFFIX] [--overwrite]

Fetch and download files from gina processing stack

options:
  -h, --help            show this help message and exit
  -s SATELLITE, --satellite SATELLITE
                        Fetch data for SATELLITE
  -i SENSOR, --sensor SENSOR
                        Fetch data for SENSOR
  -f FACILITY, --facility FACILITY
                        Fetch data for FACILITY
  -p PROCESSING_LEVEL, --processing-level PROCESSING_LEVEL
                        Fetch data for PROCESSING_LEVEL
  -n, --namespace       Namespace the data (Place in sub-directories for each pass)
  -o OUTPUT, --output OUTPUT
                        Path to write data to (Default: current directory)
  -z, --done-file       Create done file
  --start-date START_DATE
                        Start date for filtering products (YYYY-MM-DD format)
  --end-date END_DATE   End date for filtering products (YYYY-MM-DD format)
  -w WILDCARD, --wildcard WILDCARD
                        Wildcard filter for filenames (only download files containing this string)
  --suffix SUFFIX       Filter by file suffix (e.g., '.png' or 'small.png')
  --overwrite           Overwrite existing files (default: skip if file exists)
```


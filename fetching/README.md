# Fetching
This directory includes sample scripts for fetching data from GINA's NRT system. 

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
  * valid options are aqua, terra, snpp, noaa19, noaa18, noaa15, metop-b
* Sensor (-i) 
  - valid options are modis,avhrr, viirs, omps, atms, cris
* Facility( -f ) 
  - valid values are uafgina for the receiving station at UAF, gilmore for the various receiving stations at gilmore, and barrow for the barrow antenna.
* Processing level (-p) 
  - most users are interested in level1 data (level1) or geotiff data (geotiff_l2), contact us at support@gina.alaska.edu if another datasets in needed, and we can offer advice.
* namespace (-n)
  - this option places each "pass" in it's own directory - this is useful if a pass is taken at two sites, and the different sites will end up in seperate directories.  Without this option the files are all placed inside the path specified in the "-o" option. 


## Examples

* To fetch all the recient GeoTiff data that goes into Feeder, with different "passes" in their own subdirectories:
```
 ./mirror_products.sh  -p geotiff_l2 -n -o ./test/ 
 tree test
test
├── AQUA.20170828.013205.dat.gz
│   └── a1.20170828.0132_true_color.tif
├── t1.17240.0112
│   ├── t1.20170828.0116_2_6_1_1.small.png
│   ├── t1.20170828.0116_2_6_1_1.tif
│   ├── t1.20170828.0116_3_6_7.small.png
│   ├── t1.20170828.0116_3_6_7.tif
│   ├── t1.20170828.0116_7_2_1_1.small.png
│   ├── t1.20170828.0116_7_2_1_1.tif
│   ├── t1.20170828.0116_true_color.small.png
│   └── t1.20170828.0116_true_color.tif
├── TERRA.20170828.011054.dat.gz
│   ├── t1.20170828.0116_2_6_1_1.small.png
│   ├── t1.20170828.0116_2_6_1_1.tif
│   ├── t1.20170828.0116_31.small.png
│   ├── t1.20170828.0116_31.tif
│   ├── t1.20170828.0116_3_6_7.small.png
│   ├── t1.20170828.0116_3_6_7.tif
│   ├── t1.20170828.0116_7_2_1_1.small.png
│   ├── t1.20170828.0116_7_2_1_1.tif
│   ├── t1.20170828.0116_true_color.small.png
│   └── t1.20170828.0116_true_color.tif
└── TERRA.20170828.042231.dat.gz
    └── t1.20170828.0422_true_color.tif
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

#!/bin/bash

# http://www.gimp.org/tutorials/Basic_Batch/
# http://registry.gimp.org/node/15187
# http://www.gimp.org/docs/python/index.html#script_fu_interface

# Tested with Gimp 2.6.11

# TODO:
#  * Let the script read and convert multiple files without restarting Gimp.
#  * Don't fail on filenames containing weird characters.
#  * Make this less ugly. :)
#  * Maybe rewrite this in Python instead of bash. It would solve most of these issues.
#  * Let the ccanalyze execution be optional

function print_help() {
	echo "Usage: ./gimp_convert_to_indexed.sh INPUT.png OUTPUT.png"
	echo "This script will use Gimp to convert an image to indexed, using an optimal 256-color palette."
}

if [ "$#" == 2 -a -f "$1" -a -n "$2" ] ; then
	# Do nothing...
	true
else
	print_help
	exit 1
fi

echo "
filename='$1'
output='$2'

#img = pdb.gimp_file_load(RUN_NONINTERACTIVE, filename, filename)
img = pdb.gimp_file_load(filename, filename)
drawable = pdb.gimp_image_get_active_drawable(img)

numcolorsbefore = pdb.plug_in_ccanalyze(img, drawable)

pdb.gimp_image_convert_indexed(img, NO_DITHER, MAKE_PALETTE, 256, FALSE, TRUE, '')

# Maybe not needed to get the drawable again, but not a bad idea either.
drawable = pdb.gimp_image_get_active_drawable(img)

numcolorsafter = pdb.plug_in_ccanalyze(img, drawable)

print 'Converted from {0} to {1} colors.'.format(numcolorsbefore, numcolorsafter)

#pdb.gimp_file_save(RUN_NONINTERACTIVE, img, drawable, output, output)
pdb.gimp_file_save(img, drawable, output, output)

#pdb.gimp_image_delete(img)
pdb.gimp_quit(TRUE)
" | gimp -i --batch-interpreter 'python-fu-eval' -b -


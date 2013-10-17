#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

# This script is also available on "GIMP Plugin Registry"
# http://registry.gimp.org/node/TODO:UPLOAD!
#
# Tested on Gimp 2.8.6 with Python 2.7.5

from gimpfu import *

def ungroup_grouplayer(img, layer):
    #if not isinstance(layer, gimp.GroupLayer):
    if not pdb.gimp_item_is_group(layer):
        gimp.message('The active layer is not a group. Please select a layer group/folder and try again.');
        return

    pdb.gimp_image_undo_group_start(img)

    # The list of layers containing this GroupLayer.
    #containing_list = layer.parent.children if layer.parent else img.layers
    # The index of this GroupLayer in the previous list.
    #index = containing_list.index(layer)
    index = pdb.gimp_image_get_item_position(img, layer)

    for child_layer in reversed(layer.children):
        pdb.gimp_image_reorder_item(img, child_layer, layer.parent, index)

    pdb.gimp_image_undo_group_end(img)


# Parameters to register()
#   name
#   blurb
#   help
#   author
#   copyright
#   date
#   menupath
#   imagetypes
#     ""  (if the plugin doesn't need an image)
#     "*" (all image types)
#     "RGB*"
#     "RGB, RGBA"
#     "GRAY, GRAYA"
#     and maybe others
#   params
#     The tuple format is:
#     (type, name, description, default [, extra])
#   results
#   function

register(
    'ungroup_grouplayer',
    'Ungroup a GroupLayer',
    'Ungroup a GroupLayer. Run this on each GroupLayer to flatten the layer tree back into a layer stack.',
    u'Denilson Figueiredo de Sá',
    'Licensed under WTFPL',
    '2013-10-17',
    '<Image>/Layer/Ungroup GroupLayer',
    '*',  # What are the possible image types?
    [], # Params
    [], # Results
    ungroup_grouplayer
)

main()

#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

import math
import os
from subprocess import Popen, PIPE
import subprocess  #We will call Inkscape to compute the bounding box

import inkex

#from simplestyle import *
from copy import deepcopy
#import simpletransform

def is_group(node):
    """Check node for group tag."""
    return node.tag == inkex.addNS('g', 'svg')

def is_text(node):
    """Check node for text tag."""
    return node.tag == inkex.addNS('text', 'svg')


class KerfAdjustmentEffect(inkex.Effect):
    """
Creates a Path "outside" each of the selected paths to account for the fact
that a laser cutter's beam has some width.
    """
    def __init__(self):
        """
        Constructor.
        Defines the parms option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)

        # Define string option "--kerfmm" with "-r" shortcut and default value "0.2".
        self.OptionParser.add_option('-r', '--kerfmm', action = 'store',
          type = 'float', dest = 'kerfmm', default = 0.2,
          help = 'Amount of kerf to be adjusted for.  Must be > 0')


    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method.
        """
	kerfpx = float(self.options.kerfmm) #* 3.7795
	inkex.debug(self.options.kerfmm)
	inkex.debug(2*kerfpx)
	#build the working objects
	nodes = self.selected.values()
	todo = []
	parent = self.current_layer
	for sel in nodes:   
		id =  sel.get('id')

		dic = sel.attrib
		if(is_text(sel)):
			inkex.debug("object "+id+' is text and was ignored.  run "Path > Combine" to fix this')
		elif is_group(sel):
			inkex.debug("object "+id+' is a group and was ignored.  run "Path > Combine" to fix this')
		else:
			#Create a body clone that will be used as a union mask
			bodyMask = deepcopy(sel) 
			bodyMaskId = self.uniqueId(id)
			bodyMask.attrib["id"] = bodyMaskId
			bodyMask.attrib["style"]="opacity:1;fill:#a0a0a0;fill-opacity:0;stroke:#ff0000;stroke-width:0.5px;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:0.5"
			parent.append(bodyMask)

			#Create a copy that will be the StrokeToPath object
			kerfObject = deepcopy(sel)

			kerfObjectId = self.uniqueId(id)
			kerfObject.attrib["id"] = kerfObjectId
			kerfObject.attrib["style"]="opacity:1;fill:#a0a0a0;fill-opacity:0;stroke:#000000;stroke-width:"+str(2*kerfpx)+"px;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:0.5"
			inkex.debug(inkex.etree.tostring(sel, pretty_print=True))
			inkex.debug(inkex.etree.tostring(kerfObject, pretty_print=True))
			parent.append(kerfObject)
			todo.append({'bodyId':bodyMaskId, 'kerfId':kerfObjectId})


	#Use the command-line to call StrokeToPath on the kerfObjects, and then union them with their body Masks
	svgfile = os.path.splitext(self.svg_file)[0] + "-kerfTest.svg"

	cleanup(svgfile)
	with open(svgfile, 'wb') as copycat:
		self.document.write(copycat)
	cmdlist = []
    	cmdlist.append("inkscape")
	for t in todo:
		
		kerfId = t.get('kerfId')
		bodyId = t.get('bodyId')

		#do stroke path on the kerf
		cmdlist.append("--select=" + kerfId)
		cmdlist.append("--verb=StrokeToPath")
		#union with the body to remove the kerf lines on the wrong side
		cmdlist.append("--select=" + bodyId)
		cmdlist.append("--verb=SelectionUnion")
		cmdlist.append("--verb=EditDeselect")
	cmdlist.append("--verb=FileSave")
	cmdlist.append("--verb=FileQuit")
	cmdlist.append("-f")
	cmdlist.append(svgfile)

	run(cmdlist)

	# replace current document with content of temp copy
	xmlparser = inkex.etree.XMLParser(huge_tree=True)
	self.document = inkex.etree.parse(svgfile, parser=xmlparser)
	

	# clean up
	cleanup(svgfile)
	

def cleanup(tempfile):
    """Clean up tempfile."""
    try:
        os.remove(tempfile)
    except Exception:  # pylint: disable=broad-except
        pass

def run(cmd_format, stdin_str=None, verbose=False):
    """Run command"""
    if verbose:
        inkex.debug(cmd_format)
    out = err = None
    myproc = Popen(cmd_format, shell=False,
                   stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = myproc.communicate(stdin_str)
    if myproc.returncode == 0:
        return out
    elif err is not None:
        inkex.errormsg(err)



# Create effect instance and apply it.
effect = KerfAdjustmentEffect()
effect.affect()


# This script generates a Python interface for an Apple Macintosh Manager.
# It uses the "bgen" package to generate C code.
# The function specifications are generated by scanning the mamager's header file,
# using the "scantools" package (customized for this particular manager).

import string

# Declarations that change for each manager
MACHEADERFILE = 'Drag.h'		# The Apple header file
MODNAME = 'Drag'				# The name of the module
OBJECTNAME = 'DragObj'			# The basic name of the objects used here

# The following is *usually* unchanged but may still require tuning
MODPREFIX = MODNAME			# The prefix for module-wide routines
OBJECTTYPE = 'DragReference'	# The C type used to represent them
OBJECTPREFIX = MODPREFIX + 'Obj'	# The prefix for object methods
INPUTFILE = string.lower(MODPREFIX) + 'gen.py' # The file generated by the scanner
OUTPUTFILE = MODNAME + "module.c"	# The file generated by this program

from macsupport import *

# Create the type objects

DragReference = OpaqueByValueType(OBJECTTYPE, OBJECTPREFIX)

##CCTabHandle = OpaqueByValueType("CCTabHandle", "ResObj")
##AuxCtlHandle = OpaqueByValueType("AuxCtlHandle", "ResObj")
##ControlPartCode = Type("ControlPartCode", "h")
##DragConstraint = Type("DragConstraint", "h")
##ControlVariant = Type("ControlVariant", "h")
##IconTransformType = Type("IconTransformType", "h")
##ControlButtonGraphicAlignment = Type("ControlButtonGraphicAlignment", "h")
##ControlButtonTextAlignment = Type("ControlButtonTextAlignment", "h")
##ControlButtonTextPlacement = Type("ControlButtonTextPlacement", "h")
##ControlContentType = Type("ControlContentType", "h")
##ControlFocusPart = Type("ControlFocusPart", "h")
##
##ControlFontStyleRec = OpaqueType('ControlFontStyleRec', 'ControlFontStyle')
##ControlFontStyleRec_ptr = ControlFontStyleRec
PixMapHandle = OpaqueByValueType("PixMapHandle", "ResObj")
RgnHandle = OpaqueByValueType("RgnHandle", "ResObj")
AEDesc = OpaqueType('AEDesc')
AEDesc_ptr = AEDesc
RGBColor = OpaqueType("RGBColor", "QdRGB")

ItemReference = Type("ItemReference", "l")
FlavorType = OSTypeType("FlavorType")
DragAttributes = Type("DragAttributes", "l")
DragImageFlags = Type("DragImageFlags", "l")
DragImageTranslucency = Type("DragImageTranslucency", "l")
DragRegionMessage = Type("DragRegionMessage", "h")
ZoomAcceleration = Type("ZoomAcceleration", "h")
FlavorFlags = Type("FlavorFlags", "l")
DragTrackingMessage = Type("DragTrackingMessage", "h")

includestuff = includestuff + """
#include <%s>""" % MACHEADERFILE + """

/* Callback glue routines */
DragTrackingHandlerUPP dragglue_TrackingHandlerUPP;
DragReceiveHandlerUPP dragglue_ReceiveHandlerUPP;
DragSendDataUPP dragglue_SendDataUPP;
#if 0
DragInputUPP dragglue_InputUPP;
DragDrawingUPP dragglue_DrawingUPP;
#endif
"""

finalstuff = finalstuff + """
static pascal OSErr
dragglue_TrackingHandler(DragTrackingMessage theMessage, WindowPtr theWindow,
                         void *handlerRefCon, DragReference theDrag)
{
	PyObject *args, *rv;
	int i;
	
	args = Py_BuildValue("hO&O&", theMessage, DragObj_New, theDrag, WinObj_WhichWindow, theWindow);
	if ( args == NULL )
		return -1;
	rv = PyEval_CallObject((PyObject *)handlerRefCon, args);
	Py_DECREF(args);
	if ( rv == NULL ) {
		fprintf(stderr, "Drag: Exception in TrackingHandler\\n");
		return -1;
	}
	i = -1;
	if ( rv == Py_None )
		i = 0;
	else
		PyArg_Parse(rv, "l", &i);
	Py_DECREF(rv);
	return i;
}

static pascal OSErr
dragglue_ReceiveHandler(WindowPtr theWindow, void *handlerRefCon,
                        DragReference theDrag)
{
	PyObject *args, *rv;
	int i;
	
	args = Py_BuildValue("O&O&", DragObj_New, theDrag, WinObj_WhichWindow, theWindow);
	if ( args == NULL )
		return -1;
	rv = PyEval_CallObject((PyObject *)handlerRefCon, args);
	Py_DECREF(args);
	if ( rv == NULL ) {
		fprintf(stderr, "Drag: Exception in ReceiveHandler\\n");
		return -1;
	}
	i = -1;
	if ( rv == Py_None )
		i = 0;
	else
		PyArg_Parse(rv, "l", &i);
	Py_DECREF(rv);
	return i;
}

static pascal OSErr
dragglue_SendData(FlavorType theType, void *dragSendRefCon,
                      ItemReference theItem, DragReference theDrag)
{
	DragObjObject *self = (DragObjObject *)dragSendRefCon;
	PyObject *args, *rv;
	int i;
	
	if ( self->sendproc == NULL )
		return -1;
	args = Py_BuildValue("O&l", PyMac_BuildOSType, theType, theItem);
	if ( args == NULL )
		return -1;
	rv = PyEval_CallObject(self->sendproc, args);
	Py_DECREF(args);
	if ( rv == NULL ) {
		fprintf(stderr, "Drag: Exception in SendDataHandler\\n");
		return -1;
	}
	i = -1;
	if ( rv == Py_None )
		i = 0;
	else
		PyArg_Parse(rv, "l", &i);
	Py_DECREF(rv);
	return i;
}

#if 0
static pascal OSErr
dragglue_Input(Point *mouse, short *modifiers,
                   void *dragSendRefCon, DragReference theDrag)
{
    return 0;
}

static pascal OSErr
dragglue_Drawing(xxxx
                   void *dragSendRefCon, DragReference theDrag)
{
    return 0;
}
#endif

"""

variablestuff = """
dragglue_TrackingHandlerUPP = NewDragTrackingHandlerProc(dragglue_TrackingHandler);
dragglue_ReceiveHandlerUPP = NewDragReceiveHandlerProc(dragglue_ReceiveHandler);
dragglue_SendDataUPP = NewDragSendDataProc(dragglue_SendData);
#if 0
dragglue_InputUPP = NewDragInputProc(dragglue_Input);
dragglue_DrawingUPP = NewDragDrawingProc(dragglue_Drawing);
#endif
"""    

class MyObjectDefinition(GlobalObjectDefinition):
	def outputCheckNewArg(self):
		Output("""if (itself == NULL) {
					PyErr_SetString(Drag_Error,"Cannot create null Drag");
					return NULL;
				}""")
	def outputFreeIt(self, itselfname):
		## Output("DisposeDrag(%s);", itselfname)
		Output("Py_XDECREF(self->sendproc);")
		## Output("Py_XDECREF(self->inputproc);")
		## Output("Py_XDECREF(self->drawingproc);")
		
	def outputStructMembers(self):
		GlobalObjectDefinition.outputStructMembers(self)
		Output("PyObject *sendproc;")
		## Output("PyObject *inputproc;")
		## Output("PyObject *drawingproc;")
		
	def outputInitStructMembers(self):
		GlobalObjectDefinition.outputInitStructMembers(self)
		Output("it->sendproc = NULL;")
		## Output("it->inputproc = NULL;")
		## Output("it->drawingproc = NULL;")
		
		
# Create the generator groups and link them
module = MacModule(MODNAME, MODPREFIX, includestuff, finalstuff, initstuff, variablestuff)
object = MyObjectDefinition(OBJECTNAME, OBJECTPREFIX, OBJECTTYPE)
module.addobject(object)

# Create the generator classes used to populate the lists
Function = OSErrFunctionGenerator
Method = OSErrMethodGenerator

# Create and populate the lists
functions = []
methods = []
execfile(INPUTFILE)

# add the populated lists to the generator groups
for f in functions: module.add(f)
for f in methods: object.add(f)

# Manual generators for the callbacks

installtracking_body = """
    PyObject *callback;
    WindowPtr theWindow = NULL;
    OSErr _err;
    
    if ( !PyArg_ParseTuple(_args, "O|O&", &callback, WinObj_Convert, &theWindow) )
    	return NULL;
    Py_INCREF(callback);	/* Cannot decref later, too bad */
    _err = InstallTrackingHandler(dragglue_TrackingHandlerUPP, theWindow, (void *)callback);
	if (_err != noErr) return PyMac_Error(_err);
	Py_INCREF(Py_None);
	return Py_None;
"""
installtracking = ManualGenerator("InstallTrackingHandler", installtracking_body)
module.add(installtracking)

installreceive_body = """
    PyObject *callback;
    WindowPtr theWindow = NULL;
    OSErr _err;
    
    if ( !PyArg_ParseTuple(_args, "O|O&", &callback, WinObj_Convert, &theWindow) )
    	return NULL;
    Py_INCREF(callback);	/* Cannot decref later, too bad */
    _err = InstallReceiveHandler(dragglue_ReceiveHandlerUPP, theWindow, (void *)callback);
	if (_err != noErr) return PyMac_Error(_err);
	Py_INCREF(Py_None);
	return Py_None;
"""
installreceive = ManualGenerator("InstallReceiveHandler", installreceive_body)
module.add(installreceive)

removetracking_body = """
    WindowPtr theWindow = NULL;
    OSErr _err;
    
    if ( !PyArg_ParseTuple(_args, "|O&", WinObj_Convert, &theWindow) )
    	return NULL;
    _err = RemoveTrackingHandler(dragglue_TrackingHandlerUPP, theWindow);
	if (_err != noErr) return PyMac_Error(_err);
	Py_INCREF(Py_None);
	return Py_None;
"""
removetracking = ManualGenerator("RemoveTrackingHandler", removetracking_body)
module.add(removetracking)

removereceive_body = """
    WindowPtr theWindow = NULL;
    OSErr _err;
    
    if ( !PyArg_ParseTuple(_args, "|O&", WinObj_Convert, &theWindow) )
    	return NULL;
    _err = RemoveReceiveHandler(dragglue_ReceiveHandlerUPP, theWindow);
	if (_err != noErr) return PyMac_Error(_err);
	Py_INCREF(Py_None);
	return Py_None;
"""
removereceive = ManualGenerator("RemoveReceiveHandler", removereceive_body)
module.add(removereceive)

# generate output (open the output file as late as possible)
SetOutputFileName(OUTPUTFILE)
module.generate()

# This script generates a Python interface for an Apple Macintosh Manager.
# It uses the "bgen" package to generate C code.
# The function specifications are generated by scanning the mamager's header file,
# using the "scantools" package (customized for this particular manager).

import string

# Declarations that change for each manager
MACHEADERFILE = 'Controls.h'		# The Apple header file
MODNAME = '_Ctl'				# The name of the module
OBJECTNAME = 'Control'			# The basic name of the objects used here

# The following is *usually* unchanged but may still require tuning
MODPREFIX = 'Ctl'			# The prefix for module-wide routines
OBJECTTYPE = OBJECTNAME + 'Handle'	# The C type used to represent them
OBJECTPREFIX = MODPREFIX + 'Obj'	# The prefix for object methods
INPUTFILE = string.lower(MODPREFIX) + 'gen.py' # The file generated by the scanner
OUTPUTFILE = MODNAME + "module.c"	# The file generated by this program

from macsupport import *

# Create the type objects

ControlHandle = OpaqueByValueType(OBJECTTYPE, OBJECTPREFIX)
ControlRef = ControlHandle
ExistingControlHandle = OpaqueByValueType(OBJECTTYPE, "CtlObj_WhichControl", "BUG")

RgnHandle = OpaqueByValueType("RgnHandle", "ResObj")
CCTabHandle = OpaqueByValueType("CCTabHandle", "ResObj")
AuxCtlHandle = OpaqueByValueType("AuxCtlHandle", "ResObj")
ControlPartCode = Type("ControlPartCode", "h")
DragConstraint = Type("DragConstraint", "H")
ControlVariant = Type("ControlVariant", "h")
IconTransformType = Type("IconTransformType", "h")
EventModifiers = Type("EventModifiers", "H")
ClickActivationResult = Type("ClickActivationResult", "l")
ControlButtonGraphicAlignment = Type("ControlButtonGraphicAlignment", "h")
ControlButtonTextAlignment = Type("ControlButtonTextAlignment", "h")
ControlButtonTextPlacement = Type("ControlButtonTextPlacement", "h")
ControlContentType = Type("ControlContentType", "h")
ControlFocusPart = Type("ControlFocusPart", "h")

ControlFontStyleRec = OpaqueType('ControlFontStyleRec', 'ControlFontStyle')
ControlFontStyleRec_ptr = ControlFontStyleRec
ControlID = OpaqueType('ControlID', 'PyControlID')
ControlID_ptr = ControlID

DragTrackingMessage = Type("DragTrackingMessage", "h")
DragReference = OpaqueByValueType("DragReference", "DragObj")

CFStringRef = OpaqueByValueType("CFStringRef", "CFStringRefObj")
CFMutableStringRef = OpaqueByValueType("CFMutableStringRef", "CFMutableStringRefObj")
CFDataRef = OpaqueByValueType("CFDataRef", "CFDataRefObj")

ControlTabSize = UInt16
ControlTabDirection = UInt16
ControlPopupArrowOrientation = UInt16
ControlPopupArrowSize = UInt16
ControlClockType = UInt16
ControlClockFlags = UInt32
ControlRoundButtonSize = SInt16
DataBrowserViewStyle = OSType
DataBrowserItemID = UInt32
DataBrowserEditCommand = UInt32
DataBrowserSelectionAnchorDirection = UInt32
DataBrowserItemState = UInt32
DataBrowserPropertyID = UInt32
DataBrowserRevealOptions = UInt8
DataBrowserSortOrder = UInt16
DataBrowserSelectionFlags = UInt32
DataBrowserPropertyFlags = UInt32
DataBrowserPropertyPart = OSType
DataBrowserTableViewColumnID = DataBrowserPropertyID
#DataBrowserTableViewColumnDesc = DataBrowserPropertyDesc
DataBrowserTableViewHiliteStyle = UInt32
DataBrowserTableViewRowIndex = UInt32
DataBrowserTableViewColumnIndex = UInt32
DataBrowserPropertyType = OSType
ControlDisclosureTriangleOrientation = UInt16

DataBrowserTableViewColumnDesc = OpaqueType("DataBrowserTableViewColumnDesc",
		"DataBrowserTableViewColumnDesc")
DataBrowserListViewColumnDesc = OpaqueType("DataBrowserListViewColumnDesc",
		"DataBrowserListViewColumnDesc")
ControlButtonContentInfo = OpaqueType("ControlButtonContentInfo",
		"ControlButtonContentInfo")
ControlButtonContentInfoPtr = ControlButtonContentInfo_ptr = ControlButtonContentInfo

ControlTabEntry_ptr = OpaqueType("ControlTabEntry", "ControlTabEntry")

ControlBevelThickness = UInt16
ControlBevelButtonBehavior = UInt16
ControlBevelButtonMenuBehavior = UInt16
ControlBevelButtonMenuPlacement = UInt16
ControlPushButtonIconAlignment = UInt16

class ControlActionDefinition(Type):
	def declare(self, name):
		Output("%s %s;", self.typeName, name)
		Output("UniversalProcPtr c_callback;")
	def passInput(self, name):
		return "myactionproc_upp"
	def cleanup(self, name):
		Output("setcallback((PyObject*)_self, kMyControlActionProcTag, actionProc, &c_callback);")

class ControlActionDefinitionNewControl(ControlActionDefinition):
	def cleanup(self, name):
		Output("setcallback(_res, kMyControlActionProcTag, liveTrackingProc, &c_callback);")

ControlActionUPP = ControlActionDefinition("PyObject*", "O")
ControlActionUPPNewControl = ControlActionDefinitionNewControl("PyObject*", "O")
ControlSliderOrientation = UInt16


includestuff = includestuff + """
#ifdef WITHOUT_FRAMEWORKS
#include <Controls.h>
#include <ControlDefinitions.h>
#else
#include <Carbon/Carbon.h>
#endif

#ifdef USE_TOOLBOX_OBJECT_GLUE
extern PyObject *_CtlObj_New(ControlHandle);
extern int _CtlObj_Convert(PyObject *, ControlHandle *);

#define CtlObj_New _CtlObj_New
#define CtlObj_Convert _CtlObj_Convert
#endif

static PyObject *CtlObj_WhichControl(ControlHandle);

#define as_Control(h) ((ControlHandle)h)
#define as_Resource(ctl) ((Handle)ctl)
#if TARGET_API_MAC_CARBON
#define GetControlRect(ctl, rectp) GetControlBounds(ctl, rectp)
#else
#define GetControlRect(ctl, rectp) (*(rectp) = ((*(ctl))->contrlRect))
#endif

#define MAXTABS 32  /* maximum number of tabs that we support in a tabs control */
/*
** Parse/generate ControlFontStyleRec records
*/
#if 0 /* Not needed */
static PyObject *
ControlFontStyle_New(ControlFontStyleRec *itself)
{

	return Py_BuildValue("hhhhhhO&O&", itself->flags, itself->font,
		itself->size, itself->style, itself->mode, itself->just,
		QdRGB_New, &itself->foreColor, QdRGB_New, &itself->backColor);
}
#endif

static int
ControlFontStyle_Convert(PyObject *v, ControlFontStyleRec *itself)
{
	return PyArg_Parse(v, "(hhhhhhO&O&)", &itself->flags,
		&itself->font, &itself->size, &itself->style, &itself->mode,
		&itself->just, QdRGB_Convert, &itself->foreColor,
		QdRGB_Convert, &itself->backColor);
}

/*
** Parse/generate ControlID records
*/
static PyObject *
PyControlID_New(ControlID *itself)
{

	return Py_BuildValue("O&l", PyMac_BuildOSType, itself->signature, itself->id);
}

static int
PyControlID_Convert(PyObject *v, ControlID *itself)
{
	return PyArg_Parse(v, "(O&l)", PyMac_GetOSType, &itself->signature, &itself->id);
}

/*
** generate DataBrowserListViewColumnDesc records
*/
static int
DataBrowserTableViewColumnDesc_Convert(PyObject *v, DataBrowserTableViewColumnDesc *itself)
{
	return PyArg_Parse(v, "(lO&l)",
	                   &itself->propertyID,
	                   PyMac_GetOSType, &itself->propertyType,
	                   &itself->propertyFlags);
}

static int
ControlButtonContentInfo_Convert(PyObject *v, ControlButtonContentInfo *itself)
{
	return PyArg_Parse(v, "(hO&)",
	                   &itself->contentType,
	                   OptResObj_Convert, &itself->u.iconSuite);
}

static int
DataBrowserListViewHeaderDesc_Convert(PyObject *v, DataBrowserListViewHeaderDesc *itself)
{
	itself->version = kDataBrowserListViewLatestHeaderDesc;
	return PyArg_Parse(v, "(HHhO&HO&O&)",
	                   &itself->minimumWidth,
	                   &itself->maximumWidth,
	                   &itself->titleOffset,
	                   CFStringRefObj_Convert, &itself->titleString,
	                   &itself->initialOrder,
	                   ControlFontStyle_Convert, &itself->btnFontStyle,
	                   ControlButtonContentInfo_Convert, &itself->btnContentInfo);
}

static int
DataBrowserListViewColumnDesc_Convert(PyObject *v, DataBrowserListViewColumnDesc *itself)
{
	return PyArg_Parse(v, "(O&O&)",
	                   DataBrowserTableViewColumnDesc_Convert, &itself->propertyDesc,
	                   DataBrowserListViewHeaderDesc_Convert, &itself->headerBtnDesc);
}

/* TrackControl and HandleControlClick callback support */
#define kMyControlActionProcTag 'ACTN'  /* not an official tag, only for internal use */
static PyObject *tracker;
static ControlActionUPP mytracker_upp;
static ControlActionUPP myactionproc_upp;
static ControlUserPaneKeyDownUPP mykeydownproc_upp;
static ControlUserPaneFocusUPP myfocusproc_upp;
static ControlUserPaneDrawUPP mydrawproc_upp;
static ControlUserPaneIdleUPP myidleproc_upp;
static ControlUserPaneHitTestUPP myhittestproc_upp;
static ControlUserPaneTrackingUPP mytrackingproc_upp;

static int settrackfunc(PyObject *); 	/* forward */
static void clrtrackfunc(void);	/* forward */
static int setcallback(PyObject *, OSType, PyObject *, UniversalProcPtr *);
"""

finalstuff = finalstuff + """
static PyObject *
CtlObj_NewUnmanaged(ControlHandle itself)
{
	ControlObject *it;
	if (itself == NULL) return PyMac_Error(resNotFound);
	it = PyObject_NEW(ControlObject, &Control_Type);
	if (it == NULL) return NULL;
	it->ob_itself = itself;
	it->ob_callbackdict = NULL;
	return (PyObject *)it;
}

static PyObject *
CtlObj_WhichControl(ControlHandle c)
{
	PyObject *it;

	if (c == NULL)
		it = Py_None;
	else {
		it = (PyObject *) GetControlReference(c);
		/*
		** If the refcon is zero or doesn't point back to the Python object
		** the control is not ours. Return a temporary object.
		*/
		if (it == NULL || ((ControlObject *)it)->ob_itself != c)
			return CtlObj_NewUnmanaged(c);
	}
	Py_INCREF(it);
	return it;
}

static int
settrackfunc(PyObject *obj)
{
	if (tracker) {
		PyErr_SetString(Ctl_Error, "Tracker function in use");
		return 0;
	}
	tracker = obj;
	Py_INCREF(tracker);
	return 1;
}

static void
clrtrackfunc(void)
{
	Py_XDECREF(tracker);
	tracker = 0;
}

static pascal void
mytracker(ControlHandle ctl, short part)
{
	PyObject *args, *rv=0;

	args = Py_BuildValue("(O&i)", CtlObj_WhichControl, ctl, (int)part);
	if (args && tracker) {
		rv = PyEval_CallObject(tracker, args);
		Py_DECREF(args);
	}
	if (rv)
		Py_DECREF(rv);
	else {
		PySys_WriteStderr("TrackControl or HandleControlClick: exception in tracker function\\n");
		PyErr_Print();
	}
}

static int
setcallback(PyObject *myself, OSType which, PyObject *callback, UniversalProcPtr *uppp)
{
	ControlObject *self = (ControlObject *)myself;
	char keybuf[9];
	
	if ( which == kMyControlActionProcTag )
		*uppp = (UniversalProcPtr)myactionproc_upp;
	else if ( which == kControlUserPaneKeyDownProcTag )
		*uppp = (UniversalProcPtr)mykeydownproc_upp;
	else if ( which == kControlUserPaneFocusProcTag )
		*uppp = (UniversalProcPtr)myfocusproc_upp;
	else if ( which == kControlUserPaneDrawProcTag )
		*uppp = (UniversalProcPtr)mydrawproc_upp;
	else if ( which == kControlUserPaneIdleProcTag )
		*uppp = (UniversalProcPtr)myidleproc_upp;
	else if ( which == kControlUserPaneHitTestProcTag )
		*uppp = (UniversalProcPtr)myhittestproc_upp;
	else if ( which == kControlUserPaneTrackingProcTag )
		*uppp = (UniversalProcPtr)mytrackingproc_upp;
	else
		return -1;
	/* Only now do we test for clearing of the callback: */
	if ( callback == Py_None )
		*uppp = NULL;
	/* Create the dict if it doesn't exist yet (so we don't get such a dict for every control) */
	if ( self->ob_callbackdict == NULL )
		if ( (self->ob_callbackdict = PyDict_New()) == NULL )
			return -1;
	/* And store the Python callback */
	sprintf(keybuf, "%x", (unsigned)which);
	if (PyDict_SetItemString(self->ob_callbackdict, keybuf, callback) < 0)
		return -1;
	return 0;
}

static PyObject *
callcallback(ControlObject *self, OSType which, PyObject *arglist)
{
	char keybuf[9];
	PyObject *func, *rv;
	
	sprintf(keybuf, "%x", (unsigned)which);
	if ( self->ob_callbackdict == NULL ||
			(func = PyDict_GetItemString(self->ob_callbackdict, keybuf)) == NULL ) {
		PySys_WriteStderr("Control callback %x without callback object\\n", (unsigned)which);
		return NULL;
	}
	rv = PyEval_CallObject(func, arglist);
	if ( rv == NULL ) {
		PySys_WriteStderr("Exception in control callback %x handler\\n", (unsigned)which);
		PyErr_Print();
	}
	return rv;
}

static pascal void
myactionproc(ControlHandle control, SInt16 part)
{
	ControlObject *ctl_obj;
	PyObject *arglist, *rv;
	
	ctl_obj = (ControlObject *)CtlObj_WhichControl(control);
	arglist = Py_BuildValue("Oh", ctl_obj, part);
	rv = callcallback(ctl_obj, kMyControlActionProcTag, arglist);
	Py_XDECREF(arglist);
	Py_XDECREF(rv);
}

static pascal ControlPartCode
mykeydownproc(ControlHandle control, SInt16 keyCode, SInt16 charCode, SInt16 modifiers)
{
	ControlObject *ctl_obj;
	PyObject *arglist, *rv;
	short c_rv = 0;
	
	ctl_obj = (ControlObject *)CtlObj_WhichControl(control);
	arglist = Py_BuildValue("Ohhh", ctl_obj, keyCode, charCode, modifiers);
	rv = callcallback(ctl_obj, kControlUserPaneKeyDownProcTag, arglist);
	Py_XDECREF(arglist);
	if ( rv )
		if (!PyArg_Parse(rv, "h", &c_rv))
			PyErr_Clear();
	Py_XDECREF(rv);
	return (ControlPartCode)c_rv;
}

static pascal ControlPartCode
myfocusproc(ControlHandle control, ControlPartCode part)
{
	ControlObject *ctl_obj;
	PyObject *arglist, *rv;
	short c_rv = kControlFocusNoPart;
	
	ctl_obj = (ControlObject *)CtlObj_WhichControl(control);
	arglist = Py_BuildValue("Oh", ctl_obj, part);
	rv = callcallback(ctl_obj, kControlUserPaneFocusProcTag, arglist);
	Py_XDECREF(arglist);
	if ( rv )
		if (!PyArg_Parse(rv, "h", &c_rv))
			PyErr_Clear();
	Py_XDECREF(rv);
	return (ControlPartCode)c_rv;
}

static pascal void
mydrawproc(ControlHandle control, SInt16 part)
{
	ControlObject *ctl_obj;
	PyObject *arglist, *rv;
	
	ctl_obj = (ControlObject *)CtlObj_WhichControl(control);
	arglist = Py_BuildValue("Oh", ctl_obj, part);
	rv = callcallback(ctl_obj, kControlUserPaneDrawProcTag, arglist);
	Py_XDECREF(arglist);
	Py_XDECREF(rv);
}

static pascal void
myidleproc(ControlHandle control)
{
	ControlObject *ctl_obj;
	PyObject *arglist, *rv;
	
	ctl_obj = (ControlObject *)CtlObj_WhichControl(control);
	arglist = Py_BuildValue("O", ctl_obj);
	rv = callcallback(ctl_obj, kControlUserPaneIdleProcTag, arglist);
	Py_XDECREF(arglist);
	Py_XDECREF(rv);
}

static pascal ControlPartCode
myhittestproc(ControlHandle control, Point where)
{
	ControlObject *ctl_obj;
	PyObject *arglist, *rv;
	short c_rv = -1;

	ctl_obj = (ControlObject *)CtlObj_WhichControl(control);
	arglist = Py_BuildValue("OO&", ctl_obj, PyMac_BuildPoint, where);
	rv = callcallback(ctl_obj, kControlUserPaneHitTestProcTag, arglist);
	Py_XDECREF(arglist);
	/* Ignore errors, nothing we can do about them */
	if ( rv )
		if (!PyArg_Parse(rv, "h", &c_rv))
			PyErr_Clear();
	Py_XDECREF(rv);
	return (ControlPartCode)c_rv;
}

static pascal ControlPartCode
mytrackingproc(ControlHandle control, Point startPt, ControlActionUPP actionProc)
{
	ControlObject *ctl_obj;
	PyObject *arglist, *rv;
	short c_rv = -1;

	ctl_obj = (ControlObject *)CtlObj_WhichControl(control);
	/* We cannot pass the actionProc without lots of work */
	arglist = Py_BuildValue("OO&", ctl_obj, PyMac_BuildPoint, startPt);
	rv = callcallback(ctl_obj, kControlUserPaneTrackingProcTag, arglist);
	Py_XDECREF(arglist);
	if ( rv )
		if (!PyArg_Parse(rv, "h", &c_rv))
			PyErr_Clear();
	Py_XDECREF(rv);
	return (ControlPartCode)c_rv;
}
"""

initstuff = initstuff + """
mytracker_upp = NewControlActionUPP(mytracker);
myactionproc_upp = NewControlActionUPP(myactionproc);
mykeydownproc_upp = NewControlUserPaneKeyDownUPP(mykeydownproc);
myfocusproc_upp = NewControlUserPaneFocusUPP(myfocusproc);
mydrawproc_upp = NewControlUserPaneDrawUPP(mydrawproc);
myidleproc_upp = NewControlUserPaneIdleUPP(myidleproc);
myhittestproc_upp = NewControlUserPaneHitTestUPP(myhittestproc);
mytrackingproc_upp = NewControlUserPaneTrackingUPP(mytrackingproc);
PyMac_INIT_TOOLBOX_OBJECT_NEW(ControlHandle, CtlObj_New);
PyMac_INIT_TOOLBOX_OBJECT_CONVERT(ControlHandle, CtlObj_Convert);
"""

class MyObjectDefinition(ObjectIdentityMixin, GlobalObjectDefinition):
	def outputStructMembers(self):
		GlobalObjectDefinition.outputStructMembers(self)
		Output("PyObject *ob_callbackdict;")
	def outputCheckNewArg(self):
		Output("if (itself == NULL) return PyMac_Error(resNotFound);")
	def outputInitStructMembers(self):
		GlobalObjectDefinition.outputInitStructMembers(self)
		Output("SetControlReference(itself, (long)it);")
		Output("it->ob_callbackdict = NULL;")
	def outputCleanupStructMembers(self):
		Output("Py_XDECREF(self->ob_callbackdict);")
		Output("if (self->ob_itself)SetControlReference(self->ob_itself, (long)0); /* Make it forget about us */")

# Create the generator groups and link them
module = MacModule(MODNAME, MODPREFIX, includestuff, finalstuff, initstuff)
object = MyObjectDefinition(OBJECTNAME, OBJECTPREFIX, OBJECTTYPE)
module.addobject(object)

# Create the generator classes used to populate the lists
Function = OSErrWeakLinkFunctionGenerator
Method = OSErrWeakLinkMethodGenerator

# Create and populate the lists
functions = []
methods = []
execfile(INPUTFILE)
execfile('ctledit.py')

# add the populated lists to the generator groups
for f in functions: module.add(f)
for f in methods: object.add(f)

# Manual generator for TrackControl, due to callback ideosyncracies
trackcontrol_body = """
ControlPartCode _rv;
Point startPoint;
ControlActionUPP upp = 0;
PyObject *callback = 0;

if (!PyArg_ParseTuple(_args, "O&|O",
                      PyMac_GetPoint, &startPoint, &callback))
	return NULL;
if (callback && callback != Py_None) {
	if (PyInt_Check(callback) && PyInt_AS_LONG(callback) == -1)
		upp = (ControlActionUPP)-1;
	else {
		settrackfunc(callback);
		upp = mytracker_upp;
	}
}
_rv = TrackControl(_self->ob_itself,
                   startPoint,
                   upp);
clrtrackfunc();
_res = Py_BuildValue("h",
                     _rv);
return _res;
"""

f = ManualGenerator("TrackControl", trackcontrol_body);
f.docstring = lambda: "(Point startPoint [,trackercallback]) -> (ControlPartCode _rv)"
object.add(f)

# CJW - added 5/12/99
# Manual generator for HandleControlClick, as for TrackControl
handlecontrolclick_body = """
ControlPartCode _rv;
Point startPoint;
SInt16 modifiers;
ControlActionUPP upp = 0;
PyObject *callback = 0;

if (!PyArg_ParseTuple(_args, "O&h|O",
                      PyMac_GetPoint, &startPoint,
                      &modifiers,
                      &callback))
	return NULL;
if (callback && callback != Py_None) {
	if (PyInt_Check(callback) && PyInt_AS_LONG(callback) == -1)
		upp = (ControlActionUPP)-1;
	else {
		settrackfunc(callback);
		upp = mytracker_upp;
	}
}
_rv = HandleControlClick(_self->ob_itself,
                   startPoint,
                   modifiers,
                   upp);
clrtrackfunc();
_res = Py_BuildValue("h",
                     _rv);
return _res;
"""

f = ManualGenerator("HandleControlClick", handlecontrolclick_body);
f.docstring = lambda: "(Point startPoint, Integer modifiers, [,trackercallback]) -> (ControlPartCode _rv)"
object.add(f)

# Manual Generator for SetControlData
setcontroldata_body = """
OSErr _err;
ControlPartCode inPart;
ResType inTagName;
Size bufferSize;
Ptr buffer;

if (!PyArg_ParseTuple(_args, "hO&s#",
                      &inPart,
                      PyMac_GetOSType, &inTagName,
                      &buffer, &bufferSize))
	return NULL;

_err = SetControlData(_self->ob_itself,
	              inPart,
	              inTagName,
	              bufferSize,
                      buffer);

if (_err != noErr)
	return PyMac_Error(_err);
_res = Py_None;
return _res;
"""

f = ManualGenerator("SetControlData", setcontroldata_body);
f.docstring = lambda: "(stuff) -> None"
object.add(f)

# Manual Generator for GetControlData
getcontroldata_body = """
OSErr _err;
ControlPartCode inPart;
ResType inTagName;
Size bufferSize;
Ptr buffer;
Size outSize;

if (!PyArg_ParseTuple(_args, "hO&",
                      &inPart,
                      PyMac_GetOSType, &inTagName))
	return NULL;

/* allocate a buffer for the data */
_err = GetControlDataSize(_self->ob_itself,
	                  inPart,
	                  inTagName,
                          &bufferSize);
if (_err != noErr)
	return PyMac_Error(_err);
buffer = PyMem_NEW(char, bufferSize);
if (buffer == NULL)
	return PyErr_NoMemory();

_err = GetControlData(_self->ob_itself,
	              inPart,
	              inTagName,
	              bufferSize,
                      buffer,
                      &outSize);

if (_err != noErr) {
	PyMem_DEL(buffer);
	return PyMac_Error(_err);
}
_res = Py_BuildValue("s#", buffer, outSize);
PyMem_DEL(buffer);
return _res;
"""

f = ManualGenerator("GetControlData", getcontroldata_body);
f.docstring = lambda: "(part, type) -> String"
object.add(f)

# Manual Generator for SetControlData_Handle
setcontroldata_handle_body = """
OSErr _err;
ControlPartCode inPart;
ResType inTagName;
Handle buffer;

if (!PyArg_ParseTuple(_args, "hO&O&",
                      &inPart,
                      PyMac_GetOSType, &inTagName,
                      OptResObj_Convert, &buffer))
	return NULL;

_err = SetControlData(_self->ob_itself,
	              inPart,
	              inTagName,
	              sizeof(buffer),
                      (Ptr)&buffer);

if (_err != noErr)
	return PyMac_Error(_err);
_res = Py_None;
return _res;
"""

f = ManualGenerator("SetControlData_Handle", setcontroldata_handle_body);
f.docstring = lambda: "(ResObj) -> None"
object.add(f)

# Manual Generator for GetControlData_Handle
getcontroldata_handle_body = """
OSErr _err;
ControlPartCode inPart;
ResType inTagName;
Size bufferSize;
Handle hdl;

if (!PyArg_ParseTuple(_args, "hO&",
                      &inPart,
                      PyMac_GetOSType, &inTagName))
	return NULL;

/* Check it is handle-sized */
_err = GetControlDataSize(_self->ob_itself,
	                  inPart,
	                  inTagName,
                          &bufferSize);
if (_err != noErr)
	return PyMac_Error(_err);
if (bufferSize != sizeof(Handle)) {
	PyErr_SetString(Ctl_Error, "GetControlDataSize() != sizeof(Handle)");
	return NULL;
}

_err = GetControlData(_self->ob_itself,
	              inPart,
	              inTagName,
	              sizeof(Handle),
                      (Ptr)&hdl,
                      &bufferSize);

if (_err != noErr) {
	return PyMac_Error(_err);
}
_res = Py_BuildValue("O&", OptResObj_New, hdl);
return _res;
"""

f = ManualGenerator("GetControlData_Handle", getcontroldata_handle_body);
f.docstring = lambda: "(part, type) -> ResObj"
object.add(f)

# Manual Generator for SetControlData_Callback
setcontroldata_callback_body = """
OSErr _err;
ControlPartCode inPart;
ResType inTagName;
PyObject *callback;
UniversalProcPtr c_callback;

if (!PyArg_ParseTuple(_args, "hO&O",
                      &inPart,
                      PyMac_GetOSType, &inTagName,
                      &callback))
	return NULL;

if ( setcallback((PyObject *)_self, inTagName, callback, &c_callback) < 0 )
	return NULL;
_err = SetControlData(_self->ob_itself,
	              inPart,
	              inTagName,
	              sizeof(c_callback),
                      (Ptr)&c_callback);

if (_err != noErr)
	return PyMac_Error(_err);
_res = Py_None;
return _res;
"""

f = ManualGenerator("SetControlData_Callback", setcontroldata_callback_body);
f.docstring = lambda: "(callbackfunc) -> None"
object.add(f)

# And manual generators to get/set popup menu information
getpopupdata_body = """
PopupPrivateDataHandle hdl;

if ( (*_self->ob_itself)->contrlData == NULL ) {
	PyErr_SetString(Ctl_Error, "No contrlData handle in control");
	return 0;
}
hdl = (PopupPrivateDataHandle)(*_self->ob_itself)->contrlData;
HLock((Handle)hdl);
_res = Py_BuildValue("O&i", MenuObj_New, (*hdl)->mHandle, (int)(*hdl)->mID);
HUnlock((Handle)hdl);
return _res;
"""
f = ManualGenerator("GetPopupData", getpopupdata_body, condition="#if !TARGET_API_MAC_CARBON")
object.add(f)

setpopupdata_body = """
PopupPrivateDataHandle hdl;
MenuHandle mHandle;
short mID;

if (!PyArg_ParseTuple(_args, "O&h", MenuObj_Convert, &mHandle, &mID) )
	return 0;
if ( (*_self->ob_itself)->contrlData == NULL ) {
	PyErr_SetString(Ctl_Error, "No contrlData handle in control");
	return 0;
}
hdl = (PopupPrivateDataHandle)(*_self->ob_itself)->contrlData;
(*hdl)->mHandle = mHandle;
(*hdl)->mID = mID;
Py_INCREF(Py_None);
return Py_None;
"""
f = ManualGenerator("SetPopupData", setpopupdata_body, condition="#if !TARGET_API_MAC_CARBON")
object.add(f)


createtabscontrol_body = """\
OSStatus _err;
WindowPtr window;
Rect boundsRect;
UInt16 size;
UInt16 direction;
int i;
UInt16 numTabs;
ControlTabEntry tabArray[MAXTABS];
ControlHandle outControl;
PyObject *tabArrayObj, *tabEntry;

#ifndef CreateTabsControl
PyMac_PRECHECK(CreateTabsControl);
#endif
if (!PyArg_ParseTuple(_args, "O&O&HHO",
                      WinObj_Convert, &window,
                      PyMac_GetRect, &boundsRect,
                      &size,
                      &direction,
                      &tabArrayObj))
	return NULL;

i = PySequence_Length(tabArrayObj);
if (i == -1)
	return NULL;
if (i > MAXTABS) {
	PyErr_SetString(Ctl_Error, "Too many tabs");
	return NULL;
}
numTabs = i;
for (i=0; i<numTabs; i++) {
	tabEntry = PySequence_GetItem(tabArrayObj, i);
	if (tabEntry == NULL)
		return NULL;
	if (!PyArg_Parse(tabEntry, "(O&O&B)",
	                 ControlButtonContentInfo_Convert, &tabArray[i].icon,
	                 CFStringRefObj_Convert, &tabArray[i].name,
	                 &tabArray[i].enabled
	                 ))
		return NULL;
}

_err = CreateTabsControl(window,
                         &boundsRect,
                         size,
                         direction,
                         numTabs,
                         tabArray,
                         &outControl);
if (_err != noErr) return PyMac_Error(_err);
_res = Py_BuildValue("O&",
                     CtlObj_New, outControl);
return _res;"""

f = ManualGenerator("CreateTabsControl", createtabscontrol_body, condition="#if TARGET_API_MAC_CARBON")
f.docstring = lambda: "(WindowPtr window, Rect boundsRect, UInt16 size, UInt16 direction, ControlTabEntry tabArray) -> (ControlHandle outControl)"
module.add(f)

# generate output (open the output file as late as possible)
SetOutputFileName(OUTPUTFILE)
module.generate()

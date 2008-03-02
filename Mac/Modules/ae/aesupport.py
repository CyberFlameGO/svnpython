# This script will generate the AppleEvents interface for Python.
# It uses the "bgen" package to generate C code.
# It execs the file aegen.py which contain the function definitions
# (aegen.py was generated by aescan.py, scanning the <AppleEvents.h> header file).


from macsupport import *


AEArrayType = Type("AEArrayType", "c")
AESendMode = Type("AESendMode", "l")
AESendPriority = Type("AESendPriority", "h")
AEInteractAllowed = Type("AEInteractAllowed", "b")
AEReturnID = Type("AEReturnID", "h")
AETransactionID = Type("AETransactionID", "l")



AEEventClass = OSTypeType('AEEventClass')
AEEventID = OSTypeType('AEEventID')
AEKeyword = OSTypeType('AEKeyword')
DescType = OSTypeType('DescType')


AEDesc = OpaqueType('AEDesc')
AEDesc_ptr = OpaqueType('AEDesc')

AEAddressDesc = OpaqueType('AEAddressDesc', 'AEDesc')
AEAddressDesc_ptr = OpaqueType('AEAddressDesc', 'AEDesc')

AEDescList = OpaqueType('AEDescList', 'AEDesc')
AEDescList_ptr = OpaqueType('AEDescList', 'AEDesc')

AERecord = OpaqueType('AERecord', 'AEDesc')
AERecord_ptr = OpaqueType('AERecord', 'AEDesc')

AppleEvent = OpaqueType('AppleEvent', 'AEDesc')
AppleEvent_ptr = OpaqueType('AppleEvent', 'AEDesc')


class EHType(Type):
	def __init__(self, name = 'EventHandler', format = ''):
		Type.__init__(self, name, format)
	def declare(self, name):
		Output("AEEventHandlerUPP %s__proc__ = upp_GenericEventHandler;", name)
		Output("PyObject *%s;", name)
	def getargsFormat(self):
		return "O"
	def getargsArgs(self, name):
		return "&%s" % name
	def passInput(self, name):
		return "%s__proc__, (long)%s" % (name, name)
	def passOutput(self, name):
		return "&%s__proc__, (long *)&%s" % (name, name)
	def mkvalueFormat(self):
		return "O"
	def mkvalueArgs(self, name):
		return name
	def cleanup(self, name):
		Output("Py_INCREF(%s); /* XXX leak, but needed */", name)

class EHNoRefConType(EHType):
	def passInput(self, name):
		return "upp_GenericEventHandler"

EventHandler = EHType()
EventHandlerNoRefCon = EHNoRefConType()


IdleProcPtr = FakeType("upp_AEIdleProc")
AEIdleUPP = IdleProcPtr
EventFilterProcPtr = FakeType("(AEFilterUPP)0")
AEFilterUPP = EventFilterProcPtr
NMRecPtr = FakeType("(NMRecPtr)0")
EventHandlerProcPtr = FakeType("upp_GenericEventHandler")
AEEventHandlerUPP = EventHandlerProcPtr
AlwaysFalse = FakeType("0")


AEFunction = OSErrWeakLinkFunctionGenerator
AEMethod = OSErrWeakLinkMethodGenerator


includestuff = includestuff + """
#ifndef PyDoc_STR
#define PyDoc_STR(x) (x)
#endif
#ifdef WITHOUT_FRAMEWORKS
#include <AppleEvents.h>
#include <AEObjects.h>
#else
#include <Carbon/Carbon.h>
#endif

#ifdef USE_TOOLBOX_OBJECT_GLUE
extern PyObject *_AEDesc_New(AEDesc *);
extern int _AEDesc_Convert(PyObject *, AEDesc *);

#define AEDesc_New _AEDesc_New
#define AEDesc_NewBorrowed _AEDesc_NewBorrowed
#define AEDesc_Convert _AEDesc_Convert
#endif

typedef long refcontype;

static pascal OSErr GenericEventHandler(const AppleEvent *request, AppleEvent *reply, refcontype refcon); /* Forward */

AEEventHandlerUPP upp_GenericEventHandler;

static pascal Boolean AEIdleProc(EventRecord *theEvent, long *sleepTime, RgnHandle *mouseRgn)
{
	if ( PyOS_InterruptOccurred() )
		return 1;
#if !TARGET_API_MAC_OSX
	if ( PyMac_HandleEvent(theEvent) < 0 ) {
		PySys_WriteStderr("Exception in user event handler during AE processing\\n");
		PyErr_Clear();
	}
#endif
	return 0;
}

AEIdleUPP upp_AEIdleProc;
"""

finalstuff = finalstuff + """
static pascal OSErr
GenericEventHandler(const AppleEvent *request, AppleEvent *reply, refcontype refcon)
{
	PyObject *handler = (PyObject *)refcon;
	AEDescObject *requestObject, *replyObject;
	PyObject *args, *res;
	if ((requestObject = (AEDescObject *)AEDesc_New((AppleEvent *)request)) == NULL) {
		return -1;
	}
	if ((replyObject = (AEDescObject *)AEDesc_New(reply)) == NULL) {
		Py_DECREF(requestObject);
		return -1;
	}
	if ((args = Py_BuildValue("OO", requestObject, replyObject)) == NULL) {
		Py_DECREF(requestObject);
		Py_DECREF(replyObject);
		return -1;
	}
	res = PyEval_CallObject(handler, args);
	requestObject->ob_itself.descriptorType = 'null';
	requestObject->ob_itself.dataHandle = NULL;
	replyObject->ob_itself.descriptorType = 'null';
	replyObject->ob_itself.dataHandle = NULL;
	Py_DECREF(args);
	if (res == NULL) {
		PySys_WriteStderr("Exception in AE event handler function\\n");
		PyErr_Print();
		return -1;
	}
	Py_DECREF(res);
	return noErr;
}

PyObject *AEDesc_NewBorrowed(AEDesc *itself)
{
	PyObject *it;
	
	it = AEDesc_New(itself);
	if (it)
		((AEDescObject *)it)->ob_owned = 0;
	return (PyObject *)it;
}

"""

initstuff = initstuff + """
	upp_AEIdleProc = NewAEIdleUPP(AEIdleProc);
	upp_GenericEventHandler = NewAEEventHandlerUPP(GenericEventHandler);
	PyMac_INIT_TOOLBOX_OBJECT_NEW(AEDesc *, AEDesc_New);
	PyMac_INIT_TOOLBOX_OBJECT_NEW(AEDesc *, AEDesc_NewBorrowed);
	PyMac_INIT_TOOLBOX_OBJECT_CONVERT(AEDesc, AEDesc_Convert);
"""

module = MacModule('_AE', 'AE', includestuff, finalstuff, initstuff)

class AEDescDefinition(PEP253Mixin, GlobalObjectDefinition):
	getsetlist = [(
		'type',
		'return PyMac_BuildOSType(self->ob_itself.descriptorType);',
		None,
		'Type of this AEDesc'
		), (
		'data',
		"""
		PyObject *res;
		Size size;
		char *ptr;
		OSErr err;
		
		size = AEGetDescDataSize(&self->ob_itself);
		if ( (res = PyString_FromStringAndSize(NULL, size)) == NULL )
			return NULL;
		if ( (ptr = PyString_AsString(res)) == NULL )
			return NULL;
		if ( (err=AEGetDescData(&self->ob_itself, ptr, size)) < 0 )
			return PyMac_Error(err);	
		return res;
		""",
		None,
		'The raw data in this AEDesc'
		)]

	def __init__(self, name, prefix = None, itselftype = None):
		GlobalObjectDefinition.__init__(self, name, prefix or name, itselftype or name)
		self.argref = "*"

	def outputStructMembers(self):
		GlobalObjectDefinition.outputStructMembers(self)
		Output("int ob_owned;")
		
	def outputInitStructMembers(self):
		GlobalObjectDefinition.outputInitStructMembers(self)
		Output("it->ob_owned = 1;")
		
	def outputCleanupStructMembers(self):
		Output("if (self->ob_owned) AEDisposeDesc(&self->ob_itself);")

aedescobject = AEDescDefinition('AEDesc')
module.addobject(aedescobject)

functions = []
aedescmethods = []

execfile('aegen.py')
##execfile('aedatamodelgen.py')

# Manual generator
AutoDispose_body = """
int onoff, old;
if (!PyArg_ParseTuple(_args, "i", &onoff))
        return NULL;
old = _self->ob_owned;
_self->ob_owned = onoff;
_res = Py_BuildValue("i", old);
return _res;
"""
f = ManualGenerator("AutoDispose", AutoDispose_body)
f.docstring = lambda: "(int)->int. Automatically AEDisposeDesc the object on Python object cleanup"
aedescmethods.append(f)

for f in functions: module.add(f)
for f in aedescmethods: aedescobject.add(f)

SetOutputFileName('_AEmodule.c')
module.generate()

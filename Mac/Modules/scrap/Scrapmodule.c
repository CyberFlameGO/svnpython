
/* ========================== Module Scrap ========================== */

#include "Python.h"



#define SystemSevenOrLater 1

#include "macglue.h"
#include <Memory.h>
#include <Dialogs.h>
#include <Menus.h>
#include <Controls.h>

#include "pymactoolbox.h"

#include <Scrap.h>

/*
** Generate ScrapInfo records
*/
static PyObject *
SCRRec_New(itself)
	ScrapStuff *itself;
{

	return Py_BuildValue("lO&hhO&", itself->scrapSize,
		ResObj_New, itself->scrapHandle, itself->scrapCount, itself->scrapState,
		PyMac_BuildStr255, itself->scrapName);
}

static PyObject *Scrap_Error;

static PyObject *Scrap_InfoScrap(_self, _args)
	PyObject *_self;
	PyObject *_args;
{
	PyObject *_res = NULL;
	ScrapStuffPtr _rv;
	if (!PyArg_ParseTuple(_args, ""))
		return NULL;
	_rv = InfoScrap();
	_res = Py_BuildValue("O&",
	                     SCRRec_New, _rv);
	return _res;
}

static PyObject *Scrap_UnloadScrap(_self, _args)
	PyObject *_self;
	PyObject *_args;
{
	PyObject *_res = NULL;
	long _rv;
	if (!PyArg_ParseTuple(_args, ""))
		return NULL;
	_rv = UnloadScrap();
	if ( _rv ) return PyMac_Error((OSErr)_rv);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *Scrap_LoadScrap(_self, _args)
	PyObject *_self;
	PyObject *_args;
{
	PyObject *_res = NULL;
	long _rv;
	if (!PyArg_ParseTuple(_args, ""))
		return NULL;
	_rv = LoadScrap();
	if ( _rv ) return PyMac_Error((OSErr)_rv);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *Scrap_GetScrap(_self, _args)
	PyObject *_self;
	PyObject *_args;
{
	PyObject *_res = NULL;
	long _rv;
	Handle hDest;
	ResType theType;
	long offset;
	if (!PyArg_ParseTuple(_args, "O&O&",
	                      ResObj_Convert, &hDest,
	                      PyMac_GetOSType, &theType))
		return NULL;
	_rv = GetScrap(hDest,
	               theType,
	               &offset);
	_res = Py_BuildValue("ll",
	                     _rv,
	                     offset);
	return _res;
}

static PyObject *Scrap_ZeroScrap(_self, _args)
	PyObject *_self;
	PyObject *_args;
{
	PyObject *_res = NULL;
	long _rv;
	if (!PyArg_ParseTuple(_args, ""))
		return NULL;
	_rv = ZeroScrap();
	if ( _rv ) return PyMac_Error((OSErr)_rv);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *Scrap_PutScrap(_self, _args)
	PyObject *_self;
	PyObject *_args;
{
	PyObject *_res = NULL;
	long _rv;
	long length;
	ResType theType;
	char *source__in__;
	int source__len__;
	int source__in_len__;
	if (!PyArg_ParseTuple(_args, "O&s#",
	                      PyMac_GetOSType, &theType,
	                      &source__in__, &source__in_len__))
		return NULL;
	length = source__in_len__;
	_rv = PutScrap(length,
	               theType,
	               source__in__);
	if ( _rv ) return PyMac_Error((OSErr)_rv);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef Scrap_methods[] = {
	{"InfoScrap", (PyCFunction)Scrap_InfoScrap, 1,
	 "() -> (ScrapStuff _rv)"},
	{"UnloadScrap", (PyCFunction)Scrap_UnloadScrap, 1,
	 "() -> (OSErr)"},
	{"LoadScrap", (PyCFunction)Scrap_LoadScrap, 1,
	 "() -> (OSErr)"},
	{"GetScrap", (PyCFunction)Scrap_GetScrap, 1,
	 "(Handle hDest, ResType theType) -> (long _rv, long offset)"},
	{"ZeroScrap", (PyCFunction)Scrap_ZeroScrap, 1,
	 "() -> (OSErr)"},
	{"PutScrap", (PyCFunction)Scrap_PutScrap, 1,
	 "(ResType theType, Buffer source) -> (OSErr)"},
	{NULL, NULL, 0}
};




void initScrap()
{
	PyObject *m;
	PyObject *d;




	m = Py_InitModule("Scrap", Scrap_methods);
	d = PyModule_GetDict(m);
	Scrap_Error = PyMac_GetOSErrException();
	if (Scrap_Error == NULL ||
	    PyDict_SetItemString(d, "Error", Scrap_Error) != 0)
		Py_FatalError("can't initialize Scrap.Error");
}

/* ======================== End module Scrap ======================== */


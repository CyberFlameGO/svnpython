
/* UNIX group file access module */

#include "Python.h"
#include "structseq.h"

#include <sys/types.h>
#include <grp.h>

static PyStructSequence_Field struct_group_type_fields[] = {
   {"gr_name", "group name"},
   {"gr_passwd", "password"},
   {"gr_gid", "group id"}, 
   {"gr_mem", "group memebers"}, 
   {0}
};

PyDoc_STRVAR(struct_group__doc__,
"grp.struct_group: Results from getgr*() routines.\n\n\
This object may be accessed either as a tuple of\n\
  (gr_name,gr_passwd,gr_gid,gr_mem)\n\
or via the object attributes as named in the above tuple.\n");

static PyStructSequence_Desc struct_group_type_desc = {
   "grp.struct_group",
   struct_group__doc__,
   struct_group_type_fields,
   4,
};


static int initialized;
static PyTypeObject StructGrpType;

static PyObject *
mkgrent(struct group *p)
{
    int setIndex = 0;
    PyObject *v = PyStructSequence_New(&StructGrpType), *w;
    char **member;

    if (v == NULL)
        return NULL;

    if ((w = PyList_New(0)) == NULL) {
        Py_DECREF(v);
        return NULL;
    }
#define FSDECODE(val) PyUnicode_Decode(val, strlen(val),\
                                       Py_FileSystemDefaultEncoding,\
                                       "surrogateescape")
    for (member = p->gr_mem; *member != NULL; member++) {
        PyObject *x = FSDECODE(*member);
        if (x == NULL || PyList_Append(w, x) != 0) {
            Py_XDECREF(x);
            Py_DECREF(w);
            Py_DECREF(v);
            return NULL;
        }
        Py_DECREF(x);
    }

#define SET(i,val) PyStructSequence_SET_ITEM(v, i, val)
    SET(setIndex++, FSDECODE(p->gr_name));
#ifdef __VMS
    SET(setIndex++, Py_None);
    Py_INCREF(Py_None);
#else
    if (p->gr_passwd)
	    SET(setIndex++, FSDECODE(p->gr_passwd));
    else {
	    SET(setIndex++, Py_None);
	    Py_INCREF(Py_None);
    }
#endif
    SET(setIndex++, PyLong_FromLong((long) p->gr_gid));
    SET(setIndex++, w);
#undef SET

    if (PyErr_Occurred()) {
        Py_DECREF(v);
        return NULL;
    }

    return v;
}

static PyObject *
grp_getgrgid(PyObject *self, PyObject *pyo_id)
{
    PyObject *py_int_id;
    unsigned int gid;
    struct group *p;

    py_int_id = PyNumber_Long(pyo_id);
    if (!py_int_id)
	    return NULL;
    gid = PyLong_AS_LONG(py_int_id);
    Py_DECREF(py_int_id);

    if ((p = getgrgid(gid)) == NULL) {
	PyErr_Format(PyExc_KeyError, "getgrgid(): gid not found: %d", gid);
        return NULL;
    }
    return mkgrent(p);
}

static PyObject *
grp_getgrnam(PyObject *self, PyObject *args)
{
    char *name;
    struct group *p;
    PyObject *arg, *bytes, *retval = NULL;

    if (!PyArg_ParseTuple(args, "U:getgrnam", &arg))
        return NULL;
    if ((bytes = PyUnicode_AsEncodedString(arg, Py_FileSystemDefaultEncoding,
                                           "surrogateescape")) == NULL)
        return NULL;
    if (PyBytes_AsStringAndSize(bytes, &name, NULL) == -1)
        goto out;
    
    if ((p = getgrnam(name)) == NULL) {
	PyErr_Format(PyExc_KeyError, "getgrnam(): name not found: %s", name);
        goto out;
    }
    retval = mkgrent(p);
out:
    Py_DECREF(bytes);
    return retval;
}

static PyObject *
grp_getgrall(PyObject *self, PyObject *ignore)
{
    PyObject *d;
    struct group *p;

    if ((d = PyList_New(0)) == NULL)
        return NULL;
    setgrent();
    while ((p = getgrent()) != NULL) {
        PyObject *v = mkgrent(p);
        if (v == NULL || PyList_Append(d, v) != 0) {
            Py_XDECREF(v);
            Py_DECREF(d);
            endgrent();
            return NULL;
        }
        Py_DECREF(v);
    }
    endgrent();
    return d;
}

static PyMethodDef grp_methods[] = {
    {"getgrgid",	grp_getgrgid,	METH_O,
     "getgrgid(id) -> tuple\n\
Return the group database entry for the given numeric group ID.  If\n\
id is not valid, raise KeyError."},
    {"getgrnam",	grp_getgrnam,	METH_VARARGS,
     "getgrnam(name) -> tuple\n\
Return the group database entry for the given group name.  If\n\
name is not valid, raise KeyError."},
    {"getgrall",	grp_getgrall,	METH_NOARGS,
     "getgrall() -> list of tuples\n\
Return a list of all available group entries, in arbitrary order."},
    {NULL,		NULL}		/* sentinel */
};

PyDoc_STRVAR(grp__doc__,
"Access to the Unix group database.\n\
\n\
Group entries are reported as 4-tuples containing the following fields\n\
from the group database, in order:\n\
\n\
  name   - name of the group\n\
  passwd - group password (encrypted); often empty\n\
  gid    - numeric ID of the group\n\
  mem    - list of members\n\
\n\
The gid is an integer, name and password are strings.  (Note that most\n\
users are not explicitly listed as members of the groups they are in\n\
according to the password database.  Check both databases to get\n\
complete membership information.)");



static struct PyModuleDef grpmodule = {
	PyModuleDef_HEAD_INIT,
	"grp",
	grp__doc__,
	-1,
	grp_methods,
	NULL,
	NULL,
	NULL,
	NULL
};

PyMODINIT_FUNC
PyInit_grp(void)
{
    PyObject *m, *d;
    m = PyModule_Create(&grpmodule);
    if (m == NULL)
        return NULL;
    d = PyModule_GetDict(m);
    if (!initialized)
	    PyStructSequence_InitType(&StructGrpType, &struct_group_type_desc);
    PyDict_SetItemString(d, "struct_group", (PyObject *) &StructGrpType);
    initialized = 1;
    return m;
}

/***********************************************************
Copyright 1991-1995 by Stichting Mathematisch Centrum, Amsterdam,
The Netherlands.

                        All Rights Reserved

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation, and that the names of Stichting Mathematisch
Centrum or CWI or Corporation for National Research Initiatives or
CNRI not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior
permission.

While CWI is the initial source for this software, a modified version
is made available by the Corporation for National Research Initiatives
(CNRI) at the Internet address ftp://ftp.python.org.

STICHTING MATHEMATISCH CENTRUM AND CNRI DISCLAIM ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH
CENTRUM OR CNRI BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

******************************************************************/

/* Module definition and import implementation */

#include "allobjects.h"

/* XXX Some of the following are duplicate with allobjects.h... */
#include "node.h"
#include "token.h"
#include "graminit.h"
#include "import.h"
#include "errcode.h"
#include "sysmodule.h"
#include "bltinmodule.h"
#include "pythonrun.h"
#include "marshal.h"
#include "compile.h"
#include "eval.h"
#include "osdefs.h"
#include "importdl.h"
#ifdef macintosh
/* 'argument' is a grammar symbol, but also used in some mac header files */
#undef argument
#include "macglue.h"
#endif

#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif

extern long getmtime(); /* In getmtime.c */

/* Magic word to reject .pyc files generated by other Python versions */
/* Change for each incompatible change */
/* The value of CR and LF is incorporated so if you ever read or write
   a .pyc file in text mode the magic number will be wrong; also, the
   Apple MPW compiler swaps their values, botching string constants */
/* XXX Perhaps the magic number should be frozen and a version field
   added to the .pyc file header? */
#define MAGIC (5892 | ((long)'\r'<<16) | ((long)'\n'<<24))

object *import_modules; /* This becomes sys.modules */


/* Initialize things */

void
initimport()
{
	if (import_modules != NULL)
		fatal("duplicate initimport() call");
	if ((import_modules = newdictobject()) == NULL)
		fatal("no mem for dictionary of modules");
}


/* Un-initialize things, as good as we can */

void
doneimport()
{
	if (import_modules != NULL) {
		object *tmp = import_modules;
		import_modules = NULL;
		/* This deletes all modules from sys.modules.
		   When a module is deallocated, it in turn clears its dictionary,
		   thus hopefully breaking any circular references between modules
		   and between a module's dictionary and its functions.
		   Note that "import" will fail while we are cleaning up.
		   */
		mappingclear(tmp);
		DECREF(tmp);
	}
}


/* Helper for pythonrun.c -- return magic number */

long
get_pyc_magic()
{
	return MAGIC;
}


/* Helper for sysmodule.c -- return modules dictionary */

object *
get_modules()
{
	return import_modules;
}


/* Get the module object corresponding to a module name.
   First check the modules dictionary if there's one there,
   if not, create a new one and insert in in the modules dictionary.
   Because the former action is most common, THIS DOES NOT RETURN A
   'NEW' REFERENCE! */

object *
add_module(name)
	char *name;
{
	object *m;

	if (import_modules == NULL) {
		err_setstr(SystemError, "sys.modules has been deleted");
		return NULL;
	}
	if ((m = dictlookup(import_modules, name)) != NULL &&
	    is_moduleobject(m))
		return m;
	m = newmoduleobject(name);
	if (m == NULL)
		return NULL;
	if (dictinsert(import_modules, name, m) != 0) {
		DECREF(m);
		return NULL;
	}
	DECREF(m); /* Yes, it still exists, in modules! */

	return m;
}


/* Execute a code object in a module and return the module object
   WITH INCREMENTED REFERENCE COUNT */

object *
exec_code_module(name, co)
	char *name;
	object *co;
{
	object *m, *d, *v;

	m = add_module(name);
	if (m == NULL)
		return NULL;
	d = getmoduledict(m);
	if (dictlookup(d, "__builtins__") == NULL) {
		if (dictinsert(d, "__builtins__", getbuiltins()) != 0)
			return NULL;
	}
	/* Remember the filename as the __file__ attribute */
	if (dictinsert(d, "__file__", ((codeobject *)co)->co_filename) != 0)
		err_clear(); /* Not important enough to report */
	v = eval_code((codeobject *)co, d, d); /* XXX owner? */
	if (v == NULL)
		return NULL;
	DECREF(v);
	INCREF(m);

	return m;
}


/* Given a pathname for a Python source file, fill a buffer with the
   pathname for the corresponding compiled file.  Return the pathname
   for the compiled file, or NULL if there's no space in the buffer.
   Doesn't set an exception. */

static char *
make_compiled_pathname(pathname, buf, buflen)
	char *pathname;
	char *buf;
	int buflen;
{
	int len;

	len = strlen(pathname);
	if (len+2 > buflen)
		return NULL;
	strcpy(buf, pathname);
	strcpy(buf+len, "c");

	return buf;
}


/* Given a pathname for a Python source file, its time of last
   modification, and a pathname for a compiled file, check whether the
   compiled file represents the same version of the source.  If so,
   return a FILE pointer for the compiled file, positioned just after
   the header; if not, return NULL.
   Doesn't set an exception. */

static FILE *
check_compiled_module(pathname, mtime, cpathname)
	char *pathname;
	long mtime;
	char *cpathname;
{
	FILE *fp;
	long magic;
	long pyc_mtime;

	fp = fopen(cpathname, "rb");
	if (fp == NULL)
		return NULL;
	magic = rd_long(fp);
	if (magic != MAGIC) {
		if (verbose)
			fprintf(stderr, "# %s has bad magic\n", cpathname);
		fclose(fp);
		return NULL;
	}
	pyc_mtime = rd_long(fp);
	if (pyc_mtime != mtime) {
		if (verbose)
			fprintf(stderr, "# %s has bad mtime\n", cpathname);
		fclose(fp);
		return NULL;
	}
	if (verbose)
		fprintf(stderr, "# %s matches %s\n", cpathname, pathname);
	return fp;
}


/* Read a code object from a file and check it for validity */

static codeobject *
read_compiled_module(fp)
	FILE *fp;
{
	object *co;

	co = rd_object(fp);
	/* Ugly: rd_object() may return NULL with or without error */
	if (co == NULL || !is_codeobject(co)) {
		if (!err_occurred())
			err_setstr(ImportError,
				   "Non-code object in .pyc file");
		XDECREF(co);
		return NULL;
	}
	return (codeobject *)co;
}


/* Load a module from a compiled file, execute it, and return its
   module object WITH INCREMENTED REFERENCE COUNT */

static object *
load_compiled_module(name, cpathname, fp)
	char *name;
	char *cpathname;
	FILE *fp;
{
	long magic;
	codeobject *co;
	object *m;

	magic = rd_long(fp);
	if (magic != MAGIC) {
		err_setstr(ImportError, "Bad magic number in .pyc file");
		return NULL;
	}
	(void) rd_long(fp);
	co = read_compiled_module(fp);
	if (co == NULL)
		return NULL;
	if (verbose)
		fprintf(stderr, "import %s # precompiled from %s\n",
			name, cpathname);
	m = exec_code_module(name, (object *)co);
	DECREF(co);

	return m;
}

/* Parse a source file and return the corresponding code object */

static codeobject *
parse_source_module(pathname, fp)
	char *pathname;
	FILE *fp;
{
	codeobject *co;
	node *n;

	n = parse_file(fp, pathname, file_input);
	if (n == NULL)
		return NULL;
	co = compile(n, pathname);
	freetree(n);

	return co;
}


/* Write a compiled module to a file, placing the time of last
   modification of its source into the header.
   Errors are ignored, if a write error occurs an attempt is made to
   remove the file. */

static void
write_compiled_module(co, cpathname, mtime)
	codeobject *co;
	char *cpathname;
	long mtime;
{
	FILE *fp;

	fp = fopen(cpathname, "wb");
	if (fp == NULL) {
		if (verbose)
			fprintf(stderr,
				"# can't create %s\n", cpathname);
		return;
	}
	wr_long(MAGIC, fp);
	/* First write a 0 for mtime */
	wr_long(0L, fp);
	wr_object((object *)co, fp);
	if (ferror(fp)) {
		if (verbose)
			fprintf(stderr, "# can't write %s\n", cpathname);
		/* Don't keep partial file */
		fclose(fp);
		(void) unlink(cpathname);
		return;
	}
	/* Now write the true mtime */
	fseek(fp, 4L, 0);
	wr_long(mtime, fp);
	fflush(fp);
	fclose(fp);
	if (verbose)
		fprintf(stderr, "# wrote %s\n", cpathname);
#ifdef macintosh
	setfiletype(cpathname, 'Pyth', 'PYC ');
#endif
}


/* Load a source module from a given file and return its module
   object WITH INCREMENTED REFERENCE COUNT.  If there's a matching
   byte-compiled file, use that instead. */

static object *
load_source_module(name, pathname, fp)
	char *name;
	char *pathname;
	FILE *fp;
{
	long mtime;
	FILE *fpc;
	char buf[MAXPATHLEN+1];
	char *cpathname;
	codeobject *co;
	object *m;

	mtime = getmtime(pathname);
	cpathname = make_compiled_pathname(pathname, buf, MAXPATHLEN+1);
	if (cpathname != NULL &&
	    (fpc = check_compiled_module(pathname, mtime, cpathname))) {
		co = read_compiled_module(fpc);
		fclose(fpc);
		if (co == NULL)
			return NULL;
		if (verbose)
			fprintf(stderr, "import %s # precompiled from %s\n",
				name, cpathname);
	}
	else {
		co = parse_source_module(pathname, fp);
		if (co == NULL)
			return NULL;
		if (verbose)
			fprintf(stderr, "import %s # from %s\n",
				name, pathname);
		write_compiled_module(co, cpathname, mtime);
	}
	m = exec_code_module(name, (object *)co);
	DECREF(co);

	return m;
}


/* Search the path (default sys.path) for a module.  Return the
   corresponding filedescr struct, and (via return arguments) the
   pathname and an open file.  Return NULL if the module is not found. */

static struct filedescr *
find_module(name, path, buf, buflen, p_fp)
	char *name;
	object *path;
	/* Output parameters: */
	char *buf;
	int buflen;
	FILE **p_fp;
{
	int i, npath, len, namelen;
	struct filedescr *fdp = NULL;
	FILE *fp = NULL;

#ifdef MS_COREDLL
	if ((fp=PyWin_FindRegisteredModule(name, &fdp, buf, buflen))!=NULL) {
		*p_fp = fp;
		return fdp;
	}
#endif


	if (path == NULL)
		path = sysget("path");
	if (path == NULL || !is_listobject(path)) {
		err_setstr(ImportError,
			   "sys.path must be a list of directory names");
		return NULL;
	}
	npath = getlistsize(path);
	namelen = strlen(name);
	for (i = 0; i < npath; i++) {
		object *v = getlistitem(path, i);
		if (!is_stringobject(v))
			continue;
		len = getstringsize(v);
		if (len + 2 + namelen + import_maxsuffixsize >= buflen)
			continue; /* Too long */
		strcpy(buf, getstringvalue(v));
		if (strlen(buf) != len)
			continue; /* v contains '\0' */
#ifdef macintosh
		if ( PyMac_FindResourceModule(name, buf) ) {
			static struct filedescr resfiledescr = { "", "", PY_RESOURCE};
			
			return &resfiledescr;
		}
#endif
		if (len > 0 && buf[len-1] != SEP)
			buf[len++] = SEP;
#ifdef IMPORT_8x3_NAMES
		/* see if we are searching in directory dos_8x3 */
		if (len > 7 && !strncmp(buf + len - 8, "dos_8x3", 7)){
			int j;
			char ch;  /* limit name to eight lower-case characters */
			for (j = 0; (ch = name[j]) && j < 8; j++)
				if (isupper(ch))
					buf[len++] = tolower(ch);
				else
					buf[len++] = ch;
		}
		else /* Not in dos_8x3, use the full name */
#endif
		{
			strcpy(buf+len, name);
			len += namelen;
		}
		for (fdp = import_filetab; fdp->suffix != NULL; fdp++) {
			strcpy(buf+len, fdp->suffix);
			if (verbose > 1)
				fprintf(stderr, "# trying %s\n", buf);
			fp = fopen(buf, fdp->mode);
			if (fp != NULL)
				break;
		}
		if (fp != NULL)
			break;
	}
	if (fp == NULL) {
		char buf[256];
		sprintf(buf, "No module named %.200s", name);
		err_setstr(ImportError, buf);
		return NULL;
	}

	*p_fp = fp;
	return fdp;
}


/* Load an external module using the default search path and return
   its module object WITH INCREMENTED REFERENCE COUNT */

static object *
load_module(name)
	char *name;
{
	char buf[MAXPATHLEN+1];
	struct filedescr *fdp;
	FILE *fp = NULL;
	object *m;

	fdp = find_module(name, (object *)NULL, buf, MAXPATHLEN+1, &fp);
	if (fdp == NULL)
		return NULL;

	switch (fdp->type) {

	case PY_SOURCE:
		m = load_source_module(name, buf, fp);
		break;

	case PY_COMPILED:
		m = load_compiled_module(name, buf, fp);
		break;

	case C_EXTENSION:
		m = load_dynamic_module(name, buf, fp);
		break;

#ifdef macintosh
	case PY_RESOURCE:
		m = PyMac_LoadResourceModule(name, buf);
		break;
#endif

	default:
		err_setstr(SystemError,
			   "find_module returned unexpected result");
		m = NULL;

	}
	if ( fp )
		fclose(fp);

	return m;
}


/* Initialize a built-in module.
   Return 1 for succes, 0 if the module is not found, and -1 with
   an exception set if the initialization failed. */

static int
init_builtin(name)
	char *name;
{
	int i;
	for (i = 0; inittab[i].name != NULL; i++) {
		if (strcmp(name, inittab[i].name) == 0) {
			if (inittab[i].initfunc == NULL) {
				err_setstr(ImportError,
					   "Cannot re-init internal module");
				return -1;
			}
			if (verbose)
				fprintf(stderr, "import %s # builtin\n",
					name);
			(*inittab[i].initfunc)();
			if (err_occurred())
				return -1;
			return 1;
		}
	}
	return 0;
}


/* Frozen modules */

static struct _frozen *
find_frozen(name)
	char *name;
{
	struct _frozen *p;

	for (p = frozen_modules; ; p++) {
		if (p->name == NULL)
			return NULL;
		if (strcmp(p->name, name) == 0)
			break;
	}
	return p;
}

static object *
get_frozen_object(name)
	char *name;
{
	struct _frozen *p = find_frozen(name);

	if (p == NULL) {
		err_setstr(ImportError, "No such frozen object");
		return NULL;
	}
	return rds_object((char *)p->code, p->size);
}

/* Initialize a frozen module.
   Return 1 for succes, 0 if the module is not found, and -1 with
   an exception set if the initialization failed.
   This function is also used from frozenmain.c */

int
init_frozen(name)
	char *name;
{
	struct _frozen *p = find_frozen(name);
	object *co;
	object *m;

	if (p == NULL)
		return 0;
	if (verbose)
		fprintf(stderr, "import %s # frozen\n", name);
	co = rds_object((char *)p->code, p->size);
	if (co == NULL)
		return -1;
	if (!is_codeobject(co)) {
		DECREF(co);
		err_setstr(TypeError, "frozen object is not a code object");
		return -1;
	}
	m = exec_code_module(name, co);
	DECREF(co);
	if (m == NULL)
		return -1;
	DECREF(m);
	return 1;
}


/* Import a module, either built-in, frozen, or external, and return
   its module object WITH INCREMENTED REFERENCE COUNT */

object *
import_module(name)
	char *name;
{
	object *m;

	if (import_modules == NULL) {
		err_setstr(SystemError, "sys.modules has been deleted");
		return NULL;
	}
	if ((m = dictlookup(import_modules, name)) != NULL) {
		INCREF(m);
	}
	else {
		int i;
		if ((i = init_builtin(name)) || (i = init_frozen(name))) {
			if (i < 0)
				return NULL;
			if ((m = dictlookup(import_modules, name)) == NULL) {
			    if (err_occurred() == NULL)
			        err_setstr(SystemError,
				 "built-in module not initialized properly");
			}
			else
				INCREF(m);
		}
		else
			m = load_module(name);
	}

	return m;
}


/* Re-import a module of any kind and return its module object, WITH
   INCREMENTED REFERENCE COUNT */

object *
reload_module(m)
	object *m;
{
	char *name;
	int i;

	if (m == NULL || !is_moduleobject(m)) {
		err_setstr(TypeError, "reload() argument must be module");
		return NULL;
	}
	name = getmodulename(m);
	if (name == NULL)
		return NULL;
	if (import_modules == NULL) {
		err_setstr(SystemError, "sys.modules has been deleted");
		return NULL;
	}
	if (m != dictlookup(import_modules, name)) {
		err_setstr(ImportError, "reload() module not in sys.modules");
		return NULL;
	}
	/* Check for built-in and frozen modules */
	if ((i = init_builtin(name)) || (i = init_frozen(name))) {
		if (i < 0)
			return NULL;
		INCREF(m);
	}
	else
		m = load_module(name);
	return m;
}


/* Module 'imp' provides Python access to the primitives used for
   importing modules.
*/

static object *
imp_get_magic(self, args)
	object *self;
	object *args;
{
	char buf[4];

	if (!newgetargs(args, ""))
		return NULL;
	buf[0] = (MAGIC >>  0) & 0xff;
	buf[1] = (MAGIC >>  8) & 0xff;
	buf[2] = (MAGIC >> 16) & 0xff;
	buf[3] = (MAGIC >> 24) & 0xff;

	return newsizedstringobject(buf, 4);
}

static object *
imp_get_suffixes(self, args)
	object *self;
	object *args;
{
	object *list;
	struct filedescr *fdp;

	if (!newgetargs(args, ""))
		return NULL;
	list = newlistobject(0);
	if (list == NULL)
		return NULL;
	for (fdp = import_filetab; fdp->suffix != NULL; fdp++) {
		object *item = mkvalue("ssi",
				       fdp->suffix, fdp->mode, fdp->type);
		if (item == NULL) {
			DECREF(list);
			return NULL;
		}
		if (addlistitem(list, item) < 0) {
			DECREF(list);
			DECREF(item);
			return NULL;
		}
		DECREF(item);
	}
	return list;
}

static object *
imp_find_module(self, args)
	object *self;
	object *args;
{
	extern int fclose PROTO((FILE *));
	char *name;
	object *path = NULL;
	object *fob, *ret;
	struct filedescr *fdp;
	char pathname[MAXPATHLEN+1];
	FILE *fp;
	if (!newgetargs(args, "s|O!", &name, &Listtype, &path))
		return NULL;
	fdp = find_module(name, path, pathname, MAXPATHLEN+1, &fp);
	if (fdp == NULL)
		return NULL;
	fob = newopenfileobject(fp, pathname, fdp->mode, fclose);
	if (fob == NULL) {
		fclose(fp);
		return NULL;
	}
	ret = mkvalue("Os(ssi)",
		      fob, pathname, fdp->suffix, fdp->mode, fdp->type);
	DECREF(fob);
	return ret;
}

static object *
imp_init_builtin(self, args)
	object *self;
	object *args;
{
	char *name;
	int ret;
	object *m;
	if (!newgetargs(args, "s", &name))
		return NULL;
	ret = init_builtin(name);
	if (ret < 0)
		return NULL;
	if (ret == 0) {
		INCREF(None);
		return None;
	}
	m = add_module(name);
	XINCREF(m);
	return m;
}

static object *
imp_init_frozen(self, args)
	object *self;
	object *args;
{
	char *name;
	int ret;
	object *m;
	if (!newgetargs(args, "s", &name))
		return NULL;
	ret = init_frozen(name);
	if (ret < 0)
		return NULL;
	if (ret == 0) {
		INCREF(None);
		return None;
	}
	m = add_module(name);
	XINCREF(m);
	return m;
}

static object *
imp_get_frozen_object(self, args)
	object *self;
	object *args;
{
	char *name;

	if (!newgetargs(args, "s", &name))
		return NULL;
	return get_frozen_object(name);
}

static object *
imp_is_builtin(self, args)
	object *self;
	object *args;
{
	int i;
	char *name;
	if (!newgetargs(args, "s", &name))
		return NULL;
	for (i = 0; inittab[i].name != NULL; i++) {
		if (strcmp(name, inittab[i].name) == 0) {
			if (inittab[i].initfunc == NULL)
				return newintobject(-1);
			else
				return newintobject(1);
		}
	}
	return newintobject(0);
}

static object *
imp_is_frozen(self, args)
	object *self;
	object *args;
{
	struct _frozen *p;
	char *name;
	if (!newgetargs(args, "s", &name))
		return NULL;
	for (p = frozen_modules; ; p++) {
		if (p->name == NULL)
			break;
		if (strcmp(p->name, name) == 0)
			return newintobject(1);
	}
	return newintobject(0);
}

static FILE *
get_file(pathname, fob, mode)
	char *pathname;
	object *fob;
	char *mode;
{
	FILE *fp;
	if (fob == NULL) {
		fp = fopen(pathname, mode);
		if (fp == NULL)
			err_errno(IOError);
	}
	else {
		fp = getfilefile(fob);
		if (fp == NULL)
			err_setstr(ValueError, "bad/closed file object");
	}
	return fp;
}

static object *
imp_load_compiled(self, args)
	object *self;
	object *args;
{
	char *name;
	char *pathname;
	object *fob = NULL;
	object *m;
	FILE *fp;
	if (!newgetargs(args, "ssO!", &name, &pathname, &Filetype, &fob))
		return NULL;
	fp = get_file(pathname, fob, "rb");
	if (fp == NULL)
		return NULL;
	m = load_compiled_module(name, pathname, fp);
	return m;
}

static object *
imp_load_dynamic(self, args)
	object *self;
	object *args;
{
	char *name;
	char *pathname;
	object *fob = NULL;
	object *m;
	FILE *fp = NULL;
	if (!newgetargs(args, "ss|O!", &name, &pathname, &Filetype, &fob))
		return NULL;
	if (fob)
		fp = get_file(pathname, fob, "r");
	m = load_dynamic_module(name, pathname, fp);
	return m;
}

static object *
imp_load_source(self, args)
	object *self;
	object *args;
{
	char *name;
	char *pathname;
	object *fob = NULL;
	object *m;
	FILE *fp;
	if (!newgetargs(args, "ssO!", &name, &pathname, &Filetype, &fob))
		return NULL;
	fp = get_file(pathname, fob, "r");
	if (fp == NULL)
		return NULL;
	m = load_source_module(name, pathname, fp);
	return m;
}

#ifdef macintosh
static object *
imp_load_resource(self, args)
	object *self;
	object *args;
{
	char *name;
	char *pathname;
	object *m;

	if (!newgetargs(args, "ss", &name, &pathname))
		return NULL;
	m = PyMac_LoadResourceModule(name, pathname);
	return m;
}
#endif /* macintosh */

static object *
imp_new_module(self, args)
	object *self;
	object *args;
{
	char *name;
	if (!newgetargs(args, "s", &name))
		return NULL;
	return newmoduleobject(name);
}

static struct methodlist imp_methods[] = {
	{"get_frozen_object",	imp_get_frozen_object,	1},
	{"get_magic",		imp_get_magic,		1},
	{"get_suffixes",	imp_get_suffixes,	1},
	{"find_module",		imp_find_module,	1},
	{"init_builtin",	imp_init_builtin,	1},
	{"init_frozen",		imp_init_frozen,	1},
	{"is_builtin",		imp_is_builtin,		1},
	{"is_frozen",		imp_is_frozen,		1},
	{"load_compiled",	imp_load_compiled,	1},
	{"load_dynamic",	imp_load_dynamic,	1},
	{"load_source",		imp_load_source,	1},
	{"new_module",		imp_new_module,		1},
#ifdef macintosh
	{"load_resource",	imp_load_resource,	1},
#endif
	{NULL,			NULL}		/* sentinel */
};

void
initimp()
{
	object *m, *d, *v;

	m = initmodule("imp", imp_methods);
	d = getmoduledict(m);

	v = newintobject(SEARCH_ERROR);
	dictinsert(d, "SEARCH_ERROR", v);
	XDECREF(v);

	v = newintobject(PY_SOURCE);
	dictinsert(d, "PY_SOURCE", v);
	XDECREF(v);

	v = newintobject(PY_COMPILED);
	dictinsert(d, "PY_COMPILED", v);
	XDECREF(v);

	v = newintobject(C_EXTENSION);
	dictinsert(d, "C_EXTENSION", v);
	XDECREF(v);

#ifdef macintosh
	v = newintobject(PY_RESOURCE);
	dictinsert(d, "PY_RESOURCE", v);
	XDECREF(v);
#endif


	if (err_occurred())
		fatal("imp module initialization failed");
}

# Write the actual Makefile.

import os
import string

def makemakefile(outfp, makevars, files, target):
	outfp.write("# Makefile generated by freeze.py script\n\n")

	keys = makevars.keys()
	keys.sort()
	for key in keys:
		outfp.write("%s=%s\n" % (key, makevars[key]))
	outfp.write("\nall: %s\n" % target)

	deps = []
	for i in range(len(files)):
		file = files[i]
		if file[-2:] == '.c':
			base = os.path.basename(file)
			dest = base[:-2] + '.o'
			outfp.write("%s: %s\n" % (dest, file))
			outfp.write("\t$(CC) $(CFLAGS) -c %s\n" % file)
			files[i] = dest
			deps.append(dest)

	outfp.write("\n%s: %s\n" % (target, string.join(deps)))
	outfp.write("\t$(CC) %s -o %s\n" % (string.join(files), target))

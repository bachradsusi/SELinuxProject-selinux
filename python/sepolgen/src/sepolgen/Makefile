PREFIX ?= /
PYTHON ?= python
PYTHONLIBDIR ?= $(PREFIX)$(shell $(PYTHON) -c "from distutils.sysconfig import *; print(get_python_lib(1))")
PACKAGEDIR ?= $(PYTHONLIBDIR)/sepolgen

all:

install: all
	-mkdir -p $(DESTDIR)$(PACKAGEDIR)
	install -m 644 *.py $(DESTDIR)$(PACKAGEDIR)

clean:
	rm -f parser.out parsetab.py
	rm -f *~ *.pyc
	rm -rf __pycache__

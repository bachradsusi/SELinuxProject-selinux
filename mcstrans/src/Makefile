# Installation directories.
PREFIX ?= /usr
LIBDIR ?= $(PREFIX)/lib
SBINDIR ?= /sbin
INITDIR ?= /etc/rc.d/init.d
SYSTEMDDIR ?= /usr/lib/systemd

PROG_SRC=mcstrans.c  mcscolor.c  mcstransd.c  mls_level.c
PROG_OBJS= $(patsubst %.c,%.o,$(PROG_SRC))
PROG=mcstransd
INITSCRIPT=mcstrans
CFLAGS ?= -Wall -W -Wundef -Wmissing-noreturn -Wmissing-format-attribute
override CFLAGS += -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64

all: $(PROG)

$(PROG): $(PROG_OBJS)
	$(CC) $(LDFLAGS) -pie -o $@ $^ -lselinux -lcap -lpcre $(DESTDIR)$(LIBDIR)/libsepol.a

%.o:  %.c 
	$(CC) $(CFLAGS) -fPIE -c -o $@ $<

install: all
	test -d $(DESTDIR)$(SBINDIR) || install -m 755 -d $(DESTDIR)$(SBINDIR)
	install -m 755 $(PROG) $(DESTDIR)$(SBINDIR)
	test -d $(DESTDIR)$(INITDIR) || install -m 755 -d $(DESTDIR)$(INITDIR)
	install -m 755 $(INITSCRIPT).init $(DESTDIR)$(INITDIR)/$(INITSCRIPT)
	test -d $(DESTDIR)$(SYSTEMDDIR)/system || install -m 755 -d $(DESTDIR)$(SYSTEMDDIR)/system
	install -m 644 mcstrans.service $(DESTDIR)$(SYSTEMDDIR)/system/

clean: 
	-rm -f $(OBJS) $(LOBJS) $(TARGET) $(PROG) $(PROG_OBJS) *~ \#*


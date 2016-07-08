PKGNAME = rotd
COMMAND = rotd

PREFIX = /usr
BINDIR = $(PREFIX)/bin
DATADIR = $(PREFIX)/share
MANDIR = $(DATADIR)/man
MAN1DIR = $(MANDIR)/man1
LIBEXECDIR = $(PREFIX)/libexec/$(PKGNAME)
LICENSEDIR = $(DATADIR)/licenses


EXECS = rotd-wotd-en rotd-wotd-sv
EXAMPLES = example
PLUGINS = \
	events.py	\
	fortune.py	\
	gnupg.py	\
	latex.py	\
	leapsec.py	\
	solar.py	\
	summertime.py	\
	wotd.py


all: cmd
cmd: bin/rotd

bin/rotd: src/__main__.py
	@mkdir -p bin
	cp src/__main__.py $@
	sed -i 's#^LIBEXEC = .*$$#LIBEXEC = '\''$(LIBEXECDIR)'\''#' $@
	sed -i 's#%%PLUGINPATH%%#$(DATADIR)/$(PKGNAME)/plugins#' $@
	sed -i 's/^#%%%//' $@
	chmod a+x $@

install: install-all
install-all: install-base install-doc
install-base: install-cmd install-plugins install-libexec install-license
install-doc: install-man install-examples

install-cmd: bin/rotd
	mkdir -p -- "$(DESTDIR)$(BINDIR)"
	cp -- bin/rotd "$(DESTDIR)$(BINDIR)/$(COMMAND)"
	chmod 0755 -- "$(DESTDIR)$(BINDIR)/$(COMMAND)"

install-libexec:
	mkdir -p -- "$(DESTDIR)$(LIBEXECDIR)"
	cp -- $(foreach F,$(EXECS),libexec/$(F)) "$(DESTDIR)$(LIBEXECDIR)"
	cd -- "$(DESTDIR)$(LIBEXECDIR)" && chmod 0755 -- $(EXECS)

install-plugins:
	mkdir -p -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"
	cp -- $(foreach F,$(PLUGINS),src/$(F)) "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"
	cd -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins" && chmod 0644 -- $(PLUGINS)

install-man:
	mkdir -p -- "$(DESTDIR)$(MAN1DIR)"
	cp -- doc/rotd.1 "$(DESTDIR)$(MAN1DIR)/$(COMMAND).1"
	chmod 0644 -- "$(DESTDIR)$(MAN1DIR)/$(COMMAND).1"

install-examples:
	mkdir -p -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)"
	cp -- $(EXAMPLES) "$(DESTDIR)$(DATADIR)/$(PKGNAME)"
	cd -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)" && chmod 0644 -- $(EXAMPLES)

install-license:
	mkdir -p -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	cp -- LICENSE "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	chmod 0644 -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/LICENSE"

uninstall:
	-rm    -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/LICENSE"
	-cd    -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)" && rm -- $(EXAMPLES)
	-rm    -- "$(DESTDIR)$(MAN1DIR)/$(COMMAND).1"
	-cd    -- "$(DESTDIR)$(LIBEXECDIR)" && rm -- $(EXECS)
	-cd    -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins" && rm -- $(PLUGINS)
	-rm    -- "$(DESTDIR)$(BINDIR)/$(COMMAND)"
	-rmdir -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	-rmdir -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"
	-rmdir -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)"
	-rmdir -- "$(DESTDIR)$(LIBEXECDIR)"

clean:
	-rm -r bin

.PHONY: all install uninstall clean install-cmd install-doc install-license install-all
.PHONY: install-libexec install-man install-examples install-base install-plugins

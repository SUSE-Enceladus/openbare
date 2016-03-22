DESTDIR=
PREFIX=/usr
NAME=openbare
MANPATH=$(PREFIX)/share/man

.PHONY: clean tar install

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}|' *.spec | cut -d'|' -f1)

clean:
	find -name __pycache__ -exec rm -r {} +
	find -name \*.pyc -exec rm {} +

tar:  clean
	git config tar.tar.bz2.command 'bzip2'
	git archive --prefix='$(nv)/' -o '$(nv).tar.bz2' HEAD

install:
	# django application
	mkdir -p $(DESTDIR)/srv/www/$(NAME)
	cp -r library openbare static $(DESTDIR)/srv/www/$(NAME)
	# management scripts
	mkdir -p $(DESTDIR)$(PREFIX)/sbin
	cp tools/* $(DESTDIR)$(PREFIX)/sbin/
	# config
	mkdir -p $(DESTDIR)/etc/$(NAME)
	cp production-setting-templates/* $(DESTDIR)/etc/$(NAME)/
	# manpages
	mkdir -p $(DESTDIR)/$(MANPATH)/man8
	cp man/man8/*.8 $(DESTDIR)/$(MANPATH)/man8/
	gzip $(DESTDIR)/$(MANPATH)/man8/*.8

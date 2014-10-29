all:

install:
	mkdir -p ~/.weechat/python
	cp ignore_replies.py ~/.weechat/python
	ln -s ~/.weechat/python/ignore_replies.py ~/.weechat/python/autoload

.PHONY: install

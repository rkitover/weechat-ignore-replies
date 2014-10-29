# ignore_replies.py

This is a script for WeeChat to ignore replies to any nicks you have in
your ignore list. This in effect makes conversations with people you
have ignored disappear from your channels.

## installation

In WeeChat:

```
/script install ignore_replies.py
```

To install the git version:

```bash
git clone https://github.com/rkitover/weechat-ignore-replies.git
cd weechat-ignore-replies
make install
```

Then either restart WeeChat or do a:

```
/script load ignore_replies.py
```

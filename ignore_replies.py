# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Rafael Kitover <rkitover@gmail.com>
#
# Version History:
#
# 0.0.5: 01/09/2015
#   * match nicks and hosts case-insensitively
#   * better regex for matching replies
#   * fix hostmask ignores match
#   * clean up code
#   * use irc_nick infolist instead of join/part events
# 0.0.2: 10/31/2014
#   * code cleanups
#   * upload to weechat.org
# 0.0.1: 10/28/2014
#   * initial release
#   * hostmask ignores only work when there was a join from that user,
#     will be fixed later, nick ignores always work
#
# License (BSD 2-clause):
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

SCRIPT_NAME    = "ignore_replies"
SCRIPT_AUTHOR  = "Caelum <rkitover@gmail.com>"
SCRIPT_VERSION = "0.0.5"
SCRIPT_LICENSE = "BSD"
SCRIPT_DESC    = "ignores replies to ignored nicks, does NOT support hostmask ignores yet"

try:
    import weechat
except:
    print "This script must be run under WeeChat."
    print "Get WeeChat now at: http://www.weechat.org/"
    quit()

import re

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", "")

def ignore_replies(data, action, server, signal_data):
    ignores = weechat.infolist_get("irc_ignore", "", "")
    if not ignores:
        return signal_data

    channel = re.split("\s+", signal_data)[2]

    if channel[0] != '#': # channels only
        weechat.infolist_free(ignores)
        return signal_data

    buffer = weechat.info_get("irc_buffer", "%s,%s" % (server, channel))

    if not buffer: # check this is in an actual buffer/window
        weechat.infolist_free(ignores)
        return signal_data

    message = re.split("\s+", signal_data, 3)[3][1:]

    match = re.match("""
        ^
        [^a-zA-Z0-9\[\]\\{}|_`\^-]*  # non-nick chars like a (
        ([a-zA-Z0-9\[\]\\{}|_`\^-]+) # the nick chars of nick replying to
        [^a-zA-Z0-9\[\]\\{}|_`\^-]*  # closing non-nick chars like a )
        [:,]                         # char indicating reply, : or ,
        """,
        message,
        re.VERBOSE
    )

    if not match: # don't do anything for non-replies
        weechat.infolist_free(ignores)
        return signal_data

    reply_to = match.group(1)

    chan_nicks = weechat.infolist_get("irc_nick", "", "%s,%s" % (server, channel))

    nicks = []

    while weechat.infolist_next(chan_nicks):
        nicks.append({
            "name": weechat.infolist_string(chan_nicks, "name"),
            "host": weechat.infolist_string(chan_nicks, "host")
        })

    weechat.infolist_free(chan_nicks)

    if reply_to.lower() not in [n["name"].lower() for n in nicks]: # replied to is not in the channel
        weechat.infolist_free(ignores)
        return signal_data

    reply_to_host = [n["host"] for n in nicks if n["name"].lower() == reply_to.lower()][0]

    nick = weechat.info_get("irc_nick_from_host", signal_data)

    while weechat.infolist_next(ignores):
        ign_server = weechat.infolist_string(ignores, "server")
        if ign_server not in ["*",  server]:
            next
        ign_chan = weechat.infolist_string(ignores, "channel")
        if ign_chan not in ["*", channel]:
            next
        mask = weechat.infolist_string(ignores, "mask")
        if "@" in mask:
            nick_mask = None
            host_mask = mask
        else:
            nick_mask = mask
            host_mask = None

        if ((nick_mask is not None and re.match(nick_mask, reply_to,      re.I)) or
            (host_mask is not None and re.match(host_mask, reply_to_host, re.I))):
            weechat.infolist_free(ignores)
            return "" # silence message

    weechat.infolist_free(ignores)
    return signal_data

weechat.hook_modifier("irc_in_privmsg", "ignore_replies", "")

# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Rafael Kitover <rkitover@gmail.com>
#
# Version History:
#
# 0.0.1:
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
SCRIPT_VERSION = "0.0.1"
SCRIPT_LICENSE = "BSD"
SCRIPT_DESC    = "ignores replies to ignored nicks"

try:
    import weechat
except:
    print "This script must be run under WeeChat."
    print "Get WeeChat now at: http://www.weechat.org/"
    quit()

import re

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", "")

nick_hosts = {}

def track_nick_hosts(data, signal, signal_data):
    nick = weechat.info_get("irc_nick_from_host", signal_data)
    channel = re.split("\s+", signal_data)[-1]
    nick_host = re.split("\s+", signal_data)[0].split("@")[-1]
    server = signal.split(",")[0]
    if server not in nick_hosts:
        nick_hosts[server] = {}
    if channel not in nick_hosts[server]:
        nick_hosts[server][channel] = {}
    nick_hosts[server][channel][nick] = nick_host
    return weechat.WEECHAT_RC_OK

def remove_nick_host(data, signal, signal_data):
    nick = weechat.info_get("irc_nick_from_host", signal_data)
    channel = re.search("PART\s+(\S+)", signal_data).group(1)
    nick_host = re.split("\s+", signal_data)[0].split("@")[-1]
    server = signal.split(",")[0]
    if server in nick_hosts:
        if channel in nick_hosts[server]:
            if nick in nick_hosts[server][channel]:
                del nick_hosts[server][channel][nick]
            if len(nick_hosts[server][channel]) == 0:
                del nick_hosts[server][channel]
            if len(nick_hosts[server]) == 0:
                del nick_hosts[server]
    return weechat.WEECHAT_RC_OK

def ignore_replies(data, action, server, signal_data):
    ignores = weechat.infolist_get("irc_ignore", "", "")
    if not ignores:
        return signal_data

    channel = re.split("\s+", signal_data)[2]

    if channel[0] != '#': # channels only
        return signal_data

    message = re.split("\s+", signal_data, 3)[3][1:]

    match = re.match("^(\S+)[^\w\s]\s", message)

    if not match: # only trigger for replies
        return signal_data

    reply_to = match.group(1)
    nick     = weechat.info_get("irc_nick_from_host", signal_data)
    buffer   = weechat.info_get("irc_buffer", "%s,%s" % (server, channel))

    if not buffer:
        return signal_data

    while weechat.infolist_next(ignores):
        ign_server = weechat.infolist_string(ignores, "server")
        if ign_server not in ["*",  server]:
            next
        ign_chan = weechat.infolist_string(ignores, "channel")
        if ign_chan not in ["*", channel]:
            next
        mask = weechat.infolist_string(ignores, "mask")
        if "@" in mask:
            nick_mask, host_mask = re.split("@", mask)
        else:
            nick_mask = mask
            host_mask = None

        if host_mask:
            try:
                reply_to_host = nick_hosts[server][channel][reply_to]
            except:
                reply_to_host = None
            
            if reply_to_host:
                if not re.match(host_mask, reply_to_host):
                    next

        if re.match(nick_mask, reply_to):
            return ""

    return signal_data

weechat.hook_modifier("irc_in_privmsg", "ignore_replies", "")
weechat.hook_signal("*,irc_raw_in_join", "track_nick_hosts", "")
weechat.hook_signal("*,irc_raw_in_part", "remove_nick_host", "")

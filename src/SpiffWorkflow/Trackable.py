# Copyright (C) 2007 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

class Slot(object):
    def __init__(self):
        self.subscribers = []

    def subscribe(self, user_func, *user_args):
        self.subscribers.append((user_func, user_args))

    def is_subscribed(self, user_func):
        return user_func in [pair[0] for pair in self.subscribers]

    def unsubscribe(self, user_func):
        remove = []
        for i, (func, user_args) in enumerate(self.subscribers):
            if func == user_func:
                remove.append(i)
        for i in remove:
            del self.subscribers[i]

    def n_subscribers(self):
        return len(self.subscribers)

    def signal_emit(self, *args, **kwargs):
        for func, user_args in self.subscribers:
            func(*args + user_args, **kwargs)


class Trackable(object):
    def __init__(self):
        self.slots = {}

    def signal_connect(self, name, func, *args):
        if not self.slots.has_key(name):
            self.slots[name] = Slot()
        self.slots[name].subscribe(func, *args)

    def signal_is_connected(self, name, func):
        if not self.slots.has_key(name):
            return False
        return self.slots[name].is_subscribed(func)

    def signal_disconnect(self, name, func):
        if not self.slots.has_key(name):
            return
        self.slots[name].unsubscribe(func)

    def signal_subscribers(self, name):
        if not self.slots.has_key(name):
            return 0
        return self.slots[name].n_subscribers()

    def signal_emit(self, name, *args, **kwargs):
        if not self.slots.has_key(name):
            return
        self.slots[name].signal_emit(*args, **kwargs)

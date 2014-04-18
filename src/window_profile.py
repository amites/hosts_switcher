#!/usr/bin/python
# coding=utf-8

import gtk
import gobject


class WindowProfile(gobject.GObject):

    def __init__(self):
        """create a popup window for creating new profile"""
        self.__gobject_init__()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Add profile")
        self.window.set_border_width(10)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        # self.window.set_size_request(240, 80)
        self.window.set_resizable(False)
        self.window.set_destroy_with_parent(True)
        self.profile_name = None

        vbox = gtk.VBox(False, 3)
        self.entry_name = gtk.Entry()
        vbox.pack_start(self.entry_name, False, False, 3)

        btnbox = gtk.HButtonBox()
        btnbox.set_layout(gtk.BUTTONBOX_END)

        btn_save = gtk.Button("Save")
        btn_cancel = gtk.Button("Cancel")

        btn_save.connect("clicked", self.on_save)
        btn_cancel.connect("clicked", self.on_cancel)

        btnbox.add(btn_save)
        btnbox.add(btn_cancel)
        vbox.pack_start(btnbox, False, False, 3)
        self.window.add(vbox)

    def show(self):
        self.window.show_all()

    def on_save(self, button):
        self.profile_name = self.entry_name.get_text()
        self.entry_name.set_text("")
        self.window.hide_all()
        self.emit("create_profile")

    def on_cancel(self, button):
        self.profile_name = None
        self.entry_name.set_text("")
        self.window.hide_all()

    def get_profile_name(self):
        return self.profile_name

gobject.type_register(WindowProfile)
gobject.signal_new("create_profile", WindowProfile, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
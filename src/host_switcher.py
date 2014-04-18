#!/usr/bin/python
# coding=utf-8

import gtk
import re
import os

WINDOW_TITLE = "Hosts Switcher"

ptn_hosts_filename = re.compile(r'^(.+)\.hosts$')

HOSTS_BACKUP_FOLDER = "/home/danshan/nutstore/hosts_backup"
HOSTS_FILE = "/etc/hosts"


class HostsSwitcher:
    def __init__(self):
        '''create a new window'''
        # we create a top level window and we set some parameters on it
        self.treeview_profile = gtk.TreeView()
        self.text_host = gtk.TextView()
        self.store_profile = gtk.ListStore(str, str)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(WINDOW_TITLE)
        self.window.set_border_width(10)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        # Here we connect the "destroy" event to a signal handler.
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)

        self.panel_main = gtk.HBox(False, 0)

        panel_left = self.build_left_panel()
        self.panel_main.pack_start(panel_left, False, False, 5)

        panel_right = self.build_right_panel()
        self.panel_main.pack_start(panel_right, True, True, 5)

        self.window.add(self.panel_main)
        self.window.show_all()

    def build_left_panel(self):
        # create a Vbox - a vertical container box
        # param: homogeneous, spacing
        panel_left = gtk.VBox(False, 5)
        panel_left.set_size_request(230, 260)

        # create a TreeView object which will work with our model (ListStore)
        store = self.create_model()
        self.treeview_profile.set_model(store)
        self.treeview_profile.set_rules_hint(True)
        # create the columns
        self.create_columns()
        profile_selection = self.treeview_profile.get_selection()
        profile_selection.set_mode(gtk.SELECTION_SINGLE)
        profile_selection.connect("changed", self.on_change_profile)
        self.treeview_profile.connect("row-activated", self.on_active_profile)

        # add the TreeView to the scrolled window
        # create a scrollable window and integrate it into the vbox
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.treeview_profile)

        panel_left.pack_start(sw, True, True, 5)

        return panel_left

    def build_right_panel(self):
        panel_right = gtk.VBox(False, 5)
        panel_right.set_size_request(500, 600)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.text_host)
        panel_right.pack_start(sw, True, True, 5)

        btn_apply = gtk.Button("Save")

        btn_apply.connect("clicked", self.on_save_hosts)

        btnbox = gtk.HButtonBox()
        btnbox.set_layout(gtk.BUTTONBOX_END)

        btnbox.add(btn_apply)
        panel_right.pack_start(btnbox, False, False, 5)

        return panel_right

    def create_model(self):
        '''create the model - a ListStore'''

        file_list = os.listdir(HOSTS_BACKUP_FOLDER)
        for file in file_list:
            matcher = ptn_hosts_filename.match(file)
            if matcher:
                # store.append([matcher.group(1), "√" if host_all_active else ""])
                self.store_profile.append([matcher.group(1), ""])
            else:
                continue
        return self.store_profile

    def create_columns(self):
        ''' create the columns '''
        # CellRendererText = an object that renders text into a gtk.TreeView cell
        renderer_text = gtk.CellRendererText()
        # column = a visible column in a gtk.TreeView widget
        # param: title, cell_renderer, zero or more attribute=column pairs
        # text = 0 -> attribute values for the cell renderer from column 0 in the treemodel
        column = gtk.TreeViewColumn("profile", renderer_text, text=0)
        # the logical column ID of the model to sort
        column.set_sort_column_id(0)
        # append the column
        self.treeview_profile.append_column(column)

        column = gtk.TreeViewColumn("", renderer_text, text=1)
        column.set_sort_column_id(1)
        column.set_max_width(200)
        self.treeview_profile.append_column(column)

    def destroy(self, widget, data=None):
        '''close the window and quit'''
        gtk.main_quit()
        return False

    def on_change_profile(self, selection):
        (model, tree_iter) = selection.get_selected()
        profile = model.get_value(tree_iter, 0)

        file_path = HOSTS_BACKUP_FOLDER + "/" + profile + ".hosts"
        content = self.read_file(file_path)
        buffer = self.text_host.get_buffer()
        buffer.set_text(content)

    def on_active_profile(self, treeview, path, view_column):

        selection = treeview.get_selection()
        (model, tree_iter) = selection.get_selected()
        profile = model.get_value(tree_iter, 0)

        for row in self.store_profile:
            if row[0] == profile:
                if "√" == row[1]:
                    row[1] = ""
                    print "deactive " + profile
                else:
                    row[1] = "√"
                    print "active " + profile

                break
            else:
                pass

        self.build_hosts()

    def on_save_hosts(self, button):
        buffer = self.text_host.get_buffer()
        content = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())

        selection = self.treeview_profile.get_selection()
        (model, tree_iter) = selection.get_selected()
        profile = model.get_value(tree_iter, 0)

        hosts_file = open(HOSTS_BACKUP_FOLDER + "/" + profile + ".hosts", "w")
        hosts_file.write(content)
        hosts_file.close()

        print "save " + profile
        self.build_hosts()

    def build_hosts(self):
        profile_actived = []
        for row in self.store_profile:
            if "√" == row[1]:
                profile_actived.append(row[0])

        hosts_filename = HOSTS_BACKUP_FOLDER + "/hosts.tmp"
        hosts_content = ""
        for profile in profile_actived:
            file_path = HOSTS_BACKUP_FOLDER + "/" + profile + ".hosts"
            content = self.read_file(file_path)

            hosts_content += "# ==== " + profile \
                             + "\n" + content + "\n" \
                             + "# ==== " + profile \
                             + "\n"

        self.write_file(hosts_filename, content, append=False)
        self.rename_file(hosts_filename, HOSTS_FILE + ".bak")

    def refresh_profiles(self):
        self.create_model()

    def read_file(self, file_path):
        """read file"""
        if not os.path.exists(file_path):
            self.show_error_dialog("File not exists: " + file_path)
            return None

        file_object = open(file_path)
        try:
            return file_object.read()
        except (IOError, OSError) as e:
            self.show_error_dialog(e.strerror)
        finally:
            file_object.close()

    def write_file(self, file_path, content, append=False):
        file_object = open(file_path, "w+" if append else "w")
        try:
            file_object.write(content)
        except (IOError, OSError) as e:
            self.show_error_dialog(e.strerror)
        finally:
            file_object.close()

    def rename_file(self, filename_from, filename_to):
        try:
            os.rename(filename_from, filename_to)
        except (IOError, OSError) as e:
            self.show_error_dialog(e.strerror)

    def show_error_dialog(self, error_info):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, error_info)
        dialog.run()
        dialog.destroy()

    @staticmethod
    def main():
        gtk.main()


if __name__ == "__main__":

    # make hosts back folder
    if not os.path.exists(HOSTS_BACKUP_FOLDER):
        os.makedirs(HOSTS_BACKUP_FOLDER)

    main_window = HostsSwitcher()
    main_window.main()

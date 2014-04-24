#!/usr/bin/python
# coding=utf-8

import gtk
import re
import os
import window_profile
import config

WINDOW_TITLE = "Hosts Switcher"

ptn_hosts_filename = re.compile(r'^(.+)\.hosts$')
ptn_profile_name = re.compile(r'^# ==== (.+?)$')


class HostsSwitcher:
    def __init__(self):

        """ create the main window """

        # make hosts backup folder
        if not os.path.exists(config.HOSTS_BACKUP_FOLDER):
            os.makedirs(config.HOSTS_BACKUP_FOLDER)

        self.systray = None

        # we create a top level window and we set some parameters on it
        self.window_add_profile = window_profile.WindowProfile()
        self.window_add_profile.connect("create_profile", self.create_profile)

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

        self.init_actived_profile()

        self.window.add(self.panel_main)
        self.setup_systray()
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

        btn_create = gtk.Button("Create")
        btn_delete = gtk.Button("Delete")

        btn_create.connect("clicked", self.click_create_profile)
        btn_delete.connect("clicked", self.click_delete_profile)

        btnbox = gtk.HButtonBox()
        btnbox.set_layout(gtk.BUTTONBOX_END)
        btnbox.add(btn_create)
        btnbox.add(btn_delete)
        panel_left.pack_start(btnbox, False, False, 5)

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
        btn_hide = gtk.Button("Hide")

        btn_apply.connect("clicked", self.click_save_hosts)
        btn_hide.connect("clicked", self.click_hide_window)

        btnbox = gtk.HButtonBox()
        btnbox.set_layout(gtk.BUTTONBOX_END)

        btnbox.add(btn_apply)
        btnbox.add(btn_hide)
        panel_right.pack_start(btnbox, False, False, 5)

        return panel_right

    def create_model(self):
        """create the model - a ListStore"""
        self.store_profile.clear()

        file_list = os.listdir(config.HOSTS_BACKUP_FOLDER)
        for file in file_list:
            matcher = ptn_hosts_filename.match(file)
            if matcher:
                # store.append([matcher.group(1), "√" if host_all_active else ""])
                self.store_profile.append([matcher.group(1), ""])
            else:
                continue
        return self.store_profile

    def create_columns(self):
        """ create the columns """
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
        """close the window and quit"""
        gtk.main_quit()
        return False

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

    def init_actived_profile(self):
        """ check actived profile """

        file_object = open(config.HOSTS_FILE)
        actived = set()
        try:
            for line in file_object.readlines():
                matcher = ptn_profile_name.match(line)
                if matcher:
                    actived.add(matcher.group(1))

        except (IOError, OSError) as e:
            self.show_error_dialog(e.strerror)
        finally:
            file_object.close()

        for row in self.store_profile:
            if row[0] in actived:
                row[1] = row[1] = "√"

    def build_hosts(self):
        profile_actived = []
        for row in self.store_profile:
            if "√" == row[1]:
                profile_actived.append(row[0])

        hosts_filename = config.HOSTS_BACKUP_FOLDER + "/hosts.tmp"
        hosts_content = ""
        for profile in profile_actived:
            file_path = self.gen_profile_path(profile)
            content = self.read_file(file_path)

            hosts_content += "# ==== " + profile \
                             + "\n" + content + "\n" \
                             + "# ==== " + profile \
                             + "\n"

        self.write_file(hosts_filename, hosts_content, append=False)
        self.rename_file(hosts_filename, config.HOSTS_FILE)

    def refresh_profiles(self):
        self.create_model()
        self.init_actived_profile()

    def show_error_dialog(self, error_msg):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, error_msg)
        dialog.run()
        dialog.destroy()

    def show_info_dialog(self, info_msg):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, info_msg)
        dialog.set_title("Prompt")
        result = (dialog.run() == gtk.RESPONSE_OK)
        dialog.destroy()
        return result

    # file opeation

    def read_file(self, file_path):
        """read file"""
        if not os.path.exists(file_path):
            self.show_error_dialog("File not exists: " + file_path)
            return None

        file_object = open(file_path)
        try:
            print "load " + file_path
            return file_object.read()
        except (IOError, OSError) as e:
            self.show_error_dialog(e.strerror)
        finally:
            file_object.close()

    def write_file(self, file_path, content, append=False):
        file_object = open(file_path, "w+" if append else "w")
        try:
            print "write " + file_path
            file_object.write(content)
        except (IOError, OSError) as e:
            self.show_error_dialog(e.strerror)
        finally:
            file_object.close()

    def rename_file(self, filename_from, filename_to):
        from_object = open(filename_from)
        to_object = open(filename_to, "w")
        try:
            print "rename " + filename_from + " to " + filename_to
            content = from_object.read()
            to_object.write(content)
            # os.rename(filename_from, filename_to)
        except (IOError, OSError) as e:
            self.show_error_dialog(e.strerror)
        finally:
            from_object.close()
            to_object.close()

    def remove_file(self, filename):
        try:
            print "delete " + filename
            os.remove(filename)
        except (IOError, OSError) as e:
            self.show_error_dialog(e.strerror)

    def create_profile(self, profile_window):
        profile_name = profile_window.get_profile_name()
        if not profile_name and not profile_name.strip():
            self.show_error_dialog("Profile name cannot be empty.")
            return

        profile_path = self.gen_profile_path(profile_name)
        if os.path.exists(profile_path):
            self.show_error_dialog("Host profile already exists: " + profile_path)
            return
        else:
            self.write_file(profile_path, "", append=False)
            self.refresh_profiles()

    def delete_profile(self, profile_name):
        profile_path = self.gen_profile_path(profile_name)
        if self.show_info_dialog("Are you sure to delete " + profile_name + "?") :
            self.remove_file(profile_path)
        self.refresh_profiles()

    # button callback

    def click_create_profile(self, button):
        """click Create Profile button"""
        self.window_add_profile.show()

    def click_delete_profile(self, button):
        """click Delete Profile button"""
        selection = self.treeview_profile.get_selection()
        (model, tree_iter) = selection.get_selected()
        if type(tree_iter) is not gtk.TreeIter:
            self.show_error_dialog("Choose a profile to be deleted.")
            return
        profile = model.get_value(tree_iter, 0)
        self.delete_profile(profile)

    def click_save_hosts(self, button):
        buffer = self.text_host.get_buffer()
        content = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())

        selection = self.treeview_profile.get_selection()
        (model, tree_iter) = selection.get_selected()
        profile = model.get_value(tree_iter, 0)

        file_path = self.gen_profile_path(profile)
        self.write_file(file_path, content, append=False)
        self.build_hosts()

    def click_hide_window(self, button):
        self.window.hide()

    def on_change_profile(self, selection):
        (model, tree_iter) = selection.get_selected()
        if type(tree_iter) is not gtk.TreeIter:
            return
        profile = model.get_value(tree_iter, 0)

        file_path = self.gen_profile_path(profile)
        content = self.read_file(file_path)
        buffer = self.text_host.get_buffer()
        buffer.set_text(content)

    def gen_profile_path(self, profile_name):
        return config.HOSTS_BACKUP_FOLDER + "/" + profile_name + ".hosts"

    # systray

    def show_hide_window(self, widget):
        if not self.window.get_property('visible'):
            self.window.show_all()
            self.window.activate()

    def setup_systray(self):
        self.systray = gtk.StatusIcon()
        self.systray.set_from_file('icon.png')
        self.systray.connect("activate", self.show_hide_window)
        self.systray.connect("popup-menu", self.systray_popup)
        self.systray.set_tooltip("Hide")
        self.systray.set_visible(True)

    def systray_popup(self, statusicon, button, activate_time):
        popup_menu = gtk.Menu()
        restore_item = gtk.MenuItem("Show window")
        restore_item.connect("activate", self.show_hide_window)
        popup_menu.append(restore_item)

        quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_item.connect("activate", self.destroy)
        popup_menu.append(quit_item)

        popup_menu.show_all()
        time = gtk.get_current_event_time()
        popup_menu.popup(None, None, None, 0, time)

    @staticmethod
    def main():
        gtk.main()


if __name__ == "__main__":

    main_window = HostsSwitcher()
    main_window.main()

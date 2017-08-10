import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import copy

from Device import *

__author__ = "Aashish Tripathee and Daniel Winklehner"
__doc__ = """A number of widgets inheriting from gi to be placed in the GUI repeatedly"""


class AddDevicesDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Add Devices", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             ("Save Changes"), Gtk.ResponseType.OK))

        self.set_default_size(450, 500)

        self.set_content_frame()

        self._devices = {}

        self._box = self.get_content_area()

        self._add_channel_frame = None

    def set_content_frame(self):

        self._content_frame = Gtk.Frame(label="Add Device / Channel", margin=4)
        self._content_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)

        self._devices_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        self._content_frame.add(self._devices_vbox)

    def add_pre_existing_devices(self, devices):

        self._devices = devices

        self._devices_models_views = Gtk.ListStore(str, str)

        self._devices_models_views.append(['new_device', '-- Add a New Device --'])
        for device_name, device in self._devices.items():
            self._devices_models_views.append([device_name, device.label()])

        self._devices_combo = Gtk.ComboBox.new_with_model_and_entry(self._devices_models_views)
        self._devices_combo.connect("changed", self.device_selection_callback)
        self._devices_combo.set_entry_text_column(1)
        self._devices_vbox.pack_start(self._devices_combo, False, False, 0)

    def add_device(self, new_device):
        self._devices[new_device.name()] = new_device

        # Don't initialize the devices yet.
        # We initialize them after the user has clicked on "Save Changes".

        self._devices_models_views.append([new_device.name(), new_device.label()])

        self._devices_combo.set_active(len(self._devices_models_views) - 1)

        self._devices_combo.show_all()

    def add_new_device_dialog(self):
        dialog = Gtk.Dialog("Add New Device", self, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

        content_area = dialog.get_content_area()

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        hbox.pack_start(Gtk.Label("Device Name"), True, True, 0)
        device_name_entry = Gtk.Entry()
        hbox.pack_start(device_name_entry, True, True, 0)
        content_area.pack_start(hbox, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        hbox.pack_start(Gtk.Label("Device Label"), True, True, 0)
        device_label_entry = Gtk.Entry()
        hbox.pack_start(device_label_entry, True, True, 0)
        content_area.pack_start(hbox, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        hbox.pack_start(Gtk.Label("Arduino ID"), True, True, 0)
        arduino_id_entry = Gtk.Entry()
        hbox.pack_start(arduino_id_entry, True, True, 0)
        content_area.pack_start(hbox, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        overview_page_checkbox = Gtk.CheckButton("Overview Page Presence")
        hbox.pack_start(overview_page_checkbox, True, True, 0)
        hbox.pack_start(arduino_id_entry, True, True, 0)
        content_area.pack_start(hbox, True, True, 0)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            device_name = device_name_entry.get_text()
            device_label = device_label_entry.get_text()
            arduino_id = arduino_id_entry.get_text()
            overview_page_presence = overview_page_checkbox.get_active()

            print("Got a new device!")

            new_device = Device(name=device_name, label=device_label, arduino_id=arduino_id)
            new_device.set_overview_page_presence(overview_page_presence)

            self.add_device(new_device)


        else:
            print("Cancelled!")

        dialog.destroy()

    def add_channel_callback(self, widget, device_name, params):

        try:
            # Default values.
            data_type, mode = float, "both"

            data_type_iter = params['data_type'].get_active_iter()

            if data_type_iter != None:
                model = params['data_type'].get_model()
                data_type, data_type_str = model[data_type_iter][:2]
                data_type = eval(data_type)

            mode_iter = params['mode'].get_active_iter()

            if mode_iter != None:
                model = params['mode'].get_model()
                mode, mode_str = model[mode_iter][:2]

            # Create a new channel.
            ch = Channel(name=params['name'].get_text(),
                         label=params['label'].get_text(),
                         message_header=params['msg_header'].get_text(),
                         upper_limit=float(params['upper_limit'].get_text()),
                         lower_limit=float(params['lower_limit'].get_text()),
                         data_type=data_type,
                         mode=mode,
                         unit=params['unit'].get_text())

            # Add the newly created channel to the correct device.

            if device_name in self._devices.keys():
                self._devices[device_name].add_channel(ch)
                device_label = self._devices[device_name].label()

            else:
                device_label = ""
        except ValueError as e:
            print(e)
            device_label = ""

        if len(device_label) > 0:
            msg_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                           Gtk.ButtonsType.OK, "Channel added successfully .")

            msg_dialog.format_secondary_text(
                "Successfully added the channel {} to device {}.".format(params['name'].get_text(), device_name))
            msg_dialog.run()

            msg_dialog.destroy()

            # Clear the Add-Channel form by loading the add-channel box again.
            self.load_add_channel_box(device_name)

        else:
            msg_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                           Gtk.ButtonsType.OK, "Channel could not be added.")

            msg_dialog.format_secondary_text("The given channel could not be added. Please try again later.")
            msg_dialog.run()

            msg_dialog.destroy()

    def load_add_channel_box(self, device_name):

        # Clear the "Add Channel" frame first.
        if self._add_channel_frame != None:
            self._box.remove(self._add_channel_frame)

        if device_name in self._devices.keys():
            device_label = "to " + self._devices[device_name].label()
        else:
            device_label = ""

        self._add_channel_frame = Gtk.Frame(label="Add a Channel {}".format(device_label), margin=4)
        self._add_channel_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)

        add_channel_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        self._add_channel_frame.add(add_channel_vbox)

        labels = ["Name", "Label", "Message Header", "Lower Limit", "Upper Limit", "Unit"]
        entries = [Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry()]

        for label, entry in zip(labels, entries):
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
            hbox.pack_start(Gtk.Label(label), True, True, 0)
            hbox.pack_start(entry, True, True, 0)
            add_channel_vbox.add(hbox)

        data_type_model_view = Gtk.ListStore(str, str)

        data_type_model_view.append(["bool", "Boolean"])
        data_type_model_view.append(["int", "Integer"])
        data_type_model_view.append(["float", "Float"])

        data_type_combo = Gtk.ComboBox.new_with_model_and_entry(data_type_model_view)
        data_type_combo.set_entry_text_column(1)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        hbox.pack_start(Gtk.Label("Data Type"), True, True, 0)
        hbox.pack_start(data_type_combo, True, True, 0)
        add_channel_vbox.add(hbox)

        mode_model_view = Gtk.ListStore(str, str)

        mode_model_view.append(["read", "Read"])
        mode_model_view.append(["write", "Write"])
        mode_model_view.append(["both", "Both"])

        mode_combo = Gtk.ComboBox.new_with_model_and_entry(mode_model_view)
        mode_combo.set_entry_text_column(1)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        hbox.pack_start(Gtk.Label("Mode"), True, True, 0)
        hbox.pack_start(mode_combo, True, True, 0)
        add_channel_vbox.add(hbox)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        add_channel_entry = Gtk.Button("Add Channel")
        add_channel_entry.connect("clicked", self.add_channel_callback, device_name,
                                  dict(name=entries[0], label=entries[1], msg_header=entries[2], lower_limit=entries[3],
                                       upper_limit=entries[4], unit=entries[5], data_type=data_type_combo,
                                       mode=mode_combo))
        hbox.pack_end(add_channel_entry, True, True, 0)
        add_channel_vbox.add(hbox)

        add_channel_vbox.pack_start(hbox, True, True, 0)

        self._box.add(self._add_channel_frame)
        self.show_all()

    def device_selection_callback(self, combo):

        tree_iter = combo.get_active_iter()

        if tree_iter != None:
            model = combo.get_model()
            device_name, device_label = model[tree_iter][:2]

            if device_name == "new_device":

                if self._add_channel_frame != None:
                    self._box.remove(self._add_channel_frame)

                # Create a new dialog to enter new device.
                self.add_new_device_dialog()
            else:
                # Dynamically load entries that allow the user to add a channel.
                print("Loading 'Add-Channel' module.")
                self.load_add_channel_box(device_name)

    def initialize(self):
        self._box.add(self._content_frame)

        self.show_all()


class EditDevicesDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Edit Devices", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             ("Save Changes"), Gtk.ResponseType.OK))

        self.set_default_size(450, 500)

        self.set_content_frame()

        self._devices = {}

        self._box = self.get_content_area()

        self._add_channel_frame = None

        self._edit_device_frame = None
        self._select_channel_frame = None
        self._edit_channel_frame = None

    def set_content_frame(self):

        self._content_frame = Gtk.Frame(label="Edit Device / Channel", margin=4)
        self._content_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)

        self._devices_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        self._content_frame.add(self._devices_vbox)

    def add_pre_existing_devices(self, devices):

        self._devices = devices

        self._devices_models_views = Gtk.ListStore(str, str)

        for device_name, device in self._devices.items():
            self._devices_models_views.append([device_name, device.label()])

        self._devices_combo = Gtk.ComboBox.new_with_model_and_entry(self._devices_models_views)
        self._devices_combo.connect("changed", self.device_selection_callback)
        self._devices_combo.set_entry_text_column(1)
        self._devices_vbox.pack_start(self._devices_combo, False, False, 0)

    def add_device(self, new_device):
        self._devices[new_device.name()] = new_device

        # Don't initialize the devices yet.
        # We initialize them after the user has clicked on "Save Changes".

        self._devices_models_views.append([new_device.name(), new_device.label()])

        self._devices_combo.set_active(len(self._devices_models_views) - 1)

        self._devices_combo.show_all()

    def add_channel_callback(self, widget, device_name, params):

        try:
            # Default values.
            data_type, mode = float, "both"

            data_type_iter = params['data_type'].get_active_iter()

            if data_type_iter != None:
                model = params['data_type'].get_model()
                data_type, data_type_str = model[data_type_iter][:2]
                data_type = eval(data_type)

            mode_iter = params['mode'].get_active_iter()

            if mode_iter != None:
                model = params['mode'].get_model()
                mode, mode_str = model[mode_iter][:2]

            # Create a new channel.
            ch = Channel(name=params['name'].get_text(),
                         label=params['label'].get_text(),
                         message_header=params['msg_header'].get_text(),
                         upper_limit=float(params['upper_limit'].get_text()),
                         lower_limit=float(params['lower_limit'].get_text()),
                         data_type=data_type,
                         mode=mode,
                         unit=params['unit'].get_text())

            # Add the newly created channel to the correct device.

            if device_name in self._devices.keys():
                self._devices[device_name].add_channel(ch)
                device_label = self._devices[device_name].label()

            else:
                device_label = ""
        except ValueError as e:
            print(e)
            device_label = ""

        if len(device_label) > 0:
            msg_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                           Gtk.ButtonsType.OK, "Channel added successfully .")

            msg_dialog.format_secondary_text(
                "Successfully added the channel {} to device {}.".format(params['name'].get_text(), device_name))
            msg_dialog.run()

            msg_dialog.destroy()

            # Clear the Add-Channel form by loading the add-channel box again.
            self.load_add_channel_box(device_name)

        else:
            msg_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                           Gtk.ButtonsType.OK, "Channel could not be added.")

            msg_dialog.format_secondary_text("The given channel could not be added. Please try again later.")
            msg_dialog.run()

            msg_dialog.destroy()

    def load_edit_device_box(self, device_name):
        # Clear the "Add Channel" frame first.
        if self._edit_device_frame != None:
            self._box.remove(self._edit_device_frame)
            self._box.remove(self._select_channel_frame)

        if device_name in self._devices.keys():
            device = self._devices[device_name]
            device_label = device.label()
        else:
            return

        self._edit_device_frame = Gtk.Frame(label="Edit {}".format(device_label))
        self._edit_device_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)

        edit_device_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        self._edit_device_frame.add(edit_device_vbox)

        labels = ["Name", "Label", "Arduino ID"]
        entries = [Gtk.Entry(), Gtk.Entry(), Gtk.Entry()]
        values = [device.name(), device.label(), device.get_arduino_id()]

        for label, entry, value in zip(labels, entries, values):
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
            hbox.pack_start(Gtk.Label(label), True, True, 0)
            entry.set_text(value)
            hbox.pack_start(entry, True, True, 0)
            edit_device_vbox.add(hbox)

        self._box.add(self._edit_device_frame)

        self._select_channel_frame = Gtk.Frame(label="Select Channel")
        self._select_channel_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)

        select_channel_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        # self._select_channel_frame.


        self.show_all()

    def load_add_channel_box(self, device_name):

        # Clear the "Add Channel" frame first.
        if self._add_channel_frame != None:
            self._box.remove(self._add_channel_frame)

        if device_name in self._devices.keys():
            device_label = "to " + self._devices[device_name].label()
        else:
            device_label = ""

        self._add_channel_frame = Gtk.Frame(label="Add a Channel {}".format(device_label), margin=4)
        self._add_channel_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)

        add_channel_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        self._add_channel_frame.add(add_channel_vbox)

        labels = ["Name", "Label", "Message Header", "Lower Limit", "Upper Limit", "Unit"]
        entries = [Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry()]

        for label, entry in zip(labels, entries):
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
            hbox.pack_start(Gtk.Label(label), True, True, 0)
            hbox.pack_start(entry, True, True, 0)
            add_channel_vbox.add(hbox)

        data_type_model_view = Gtk.ListStore(str, str)

        data_type_model_view.append(["bool", "Boolean"])
        data_type_model_view.append(["int", "Integer"])
        data_type_model_view.append(["float", "Float"])

        data_type_combo = Gtk.ComboBox.new_with_model_and_entry(data_type_model_view)
        data_type_combo.set_entry_text_column(1)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        hbox.pack_start(Gtk.Label("Data Type"), True, True, 0)
        hbox.pack_start(data_type_combo, True, True, 0)
        add_channel_vbox.add(hbox)

        mode_model_view = Gtk.ListStore(str, str)

        mode_model_view.append(["read", "Read"])
        mode_model_view.append(["write", "Write"])
        mode_model_view.append(["both", "Both"])

        mode_combo = Gtk.ComboBox.new_with_model_and_entry(mode_model_view)
        mode_combo.set_entry_text_column(1)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        hbox.pack_start(Gtk.Label("Mode"), True, True, 0)
        hbox.pack_start(mode_combo, True, True, 0)
        add_channel_vbox.add(hbox)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, margin=4)
        add_channel_entry = Gtk.Button("Add Channel")
        add_channel_entry.connect("clicked", self.add_channel_callback, device_name,
                                  dict(name=entries[0], label=entries[1], msg_header=entries[2], lower_limit=entries[3],
                                       upper_limit=entries[4], unit=entries[5], data_type=data_type_combo,
                                       mode=mode_combo))
        hbox.pack_end(add_channel_entry, True, True, 0)
        add_channel_vbox.add(hbox)

        add_channel_vbox.pack_start(hbox, True, True, 0)

        self._box.add(self._add_channel_frame)
        self.show_all()

    def device_selection_callback(self, combo):

        tree_iter = combo.get_active_iter()

        if tree_iter != None:
            model = combo.get_model()
            device_name, device_label = model[tree_iter][:2]

            # Dynamically load entries that allow the user to add a channel.
            print("Loading 'Add-Channel' module.")
            # self.load_add_channel_box(device_name)
            self.load_edit_device_box(device_name)

    def initialize(self):
        self._box.add(self._content_frame)

        self.show_all()


class PlottingChannelsDialog(Gtk.Dialog):

    def __init__(self, parent, tree_store, selections=[]):

        Gtk.Dialog.__init__(self, "Select Plotting Channels", parent, 0,
                            (("Save Changes"), Gtk.ResponseType.OK,
                             ))

        self.set_default_size(450, 700)
        print(selections)
        self._tree_store = tree_store
        self._box = self.get_content_area()
        self._selections = copy.deepcopy(list(selections))

        self.setup_tree_view()
        self.setup_display()

        print("The selection is", self._selections)

        self._box.show_all()

    def setup_display(self):

        self._select_channels_frame = Gtk.Frame(label="Edit Device / Channel", margin=4)
        self._select_channels_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)

        self._select_channels_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        self._select_channels_box.set_size_request(450, 600)

        self._tree_view.set_size_request(450, 600)
        self._select_channels_box.add(self._tree_view)

        self._select_channels_frame.add(self._select_channels_box)

        self._box.pack_start(self._select_channels_frame, True, True, 0)

    def get_selection(self):
        return self._selections

    def on_channel_toggle(self, cell, path, store, *ignore):

        if path is not None:

            it = store.get_iter(path)

            # print "The current state is", store[it][0].get_active()

            # store[it][0].set_active(not store[it][0].get_active())
            store[path][0] = not store[path][0]

            # print "After changing it, the updated state is", store[it][0].get_active()

            # Find out which channel it was.
            device_name = store.get_value(store.get_iter(path), 3)

            if device_name == store.get_value(store.get_iter(path), 4):
                # This means the users selected a checkbox for a device.
                # Activate all channels under this device.
                pass

            else:
                channel_name = store.get_value(store.get_iter(path), 4)

                print("toggled for ", device_name, channel_name)

                if store[it][0]:
                    # self.show_plotting_frame(device_name, channel_name)
                    self._selections.append((device_name, channel_name))
                else:
                    # self.remove_plotting_frame(device_name, channel_name)

                    print((device_name, channel_name), (device_name, channel_name) in self._selections, self._selections)

                    if (device_name, channel_name) in self._selections:
                        index = self._selections.index((device_name, channel_name))
                        print(index)
                        del self._selections[index]

        self._tree_view.show_all()

    def setup_tree_view(self):

        self._tree_view = Gtk.TreeView(self._tree_store)

        checkbox_title = Gtk.CellRendererToggle()
        checkbox_title.connect("toggled", self.on_channel_toggle, self._tree_store)

        text_title = Gtk.CellRendererText()

        column1 = Gtk.TreeViewColumn("Select", checkbox_title, active=0)
        self._tree_view.append_column(column1)

        column2 = Gtk.TreeViewColumn("Label", text_title, markup=1)
        self._tree_view.append_column(column2)



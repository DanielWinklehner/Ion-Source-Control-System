import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

__author__ = "Aashish Tripathee and Daniel Winklehner"
__doc__ = """A number of widgets inheriting from gi to be placed in the GUI repeatedly"""


class FrontPageDisplayValue(Gtk.Frame):
    """
    Simple widget with two labels and a entry box to display a single value
    """

    def __init__(self, name="Channel N/A", unit="N/A", displayformat=".2f", set_flag=False, parent_channel=None):
        """
        :param name:
        :param unit:
        :param set_flag: flag whether this is a set or a read channel
        """

        Gtk.Frame.__init__(self)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4, margin=4)

        self.name_label = Gtk.Label(name)
        self.unit_label = Gtk.Label(unit)
        self.value_entry = Gtk.Entry()
        self.value_entry.set_size_request(60, 40)

        self.set_flag = set_flag
        self.displayformat = displayformat

        self.add(hbox)

        hbox.pack_start(self.name_label, True, True, 0)
        hbox.pack_start(self.value_entry, True, True, 0)
        hbox.pack_start(self.unit_label, True, True, 0)

        if not self.set_flag:
            self.value_entry.set_sensitive(False)


        self._parent_channel = parent_channel

    def get_displayformat(self):
        """
        :return: displayformat
        """

        return self.displayformat

    def get_name(self):
        """
        Returns the name label as str
        :return: name
        """

        return self.name_label.get_text()

    def get_unit(self):
        """
        Returns the name label as str
        :return: unit
        """

        return self.unit_label.get_text()

    def get_value(self):
        """
        Returns the value entries value as float
        :return: value
        """

        return float(self.value_entry.get_text())

    def set_displayformat(self, displayformat):
        """
        :param displayformat:
        :return:
        """

        self.displayformat = displayformat

        return 0

    def set_name(self, name_str):
        """
        Returns the name label as str
        :return:
        """

        self.name_label.set_text(name_str)

        return 0

    def set_unit(self, unit_str):
        """
        Returns the name label as str
        :return:
        """

        self.unit_label.set_text(unit_str)

        return 0

    def set_value(self, value):
        """
        Sets the value in the value entry
        :param value:
        :return:
        """
        self.value_entry.set_text("{0:{1}}".format(value, self.displayformat))

        return 0

    def get_parent_channel(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._parent_channel


class FrontPageDeviceFrame(Gtk.Frame):
    """
    Simple widget with two labels and a entry box to display a single value
    """

    def __init__(self, label="Device N/A"):
        """
        :param label:
        """

        Gtk.Frame.__init__(self, label=label, margin=4)
        self.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        self.add(self.vbox)

    def get_label_text(self):
        """
        Returns the name label as str
        :return: name
        """

        return self.get_label()

    def pack_start(self, *args, **kwargs):
        """
        Wrapper around pack_start for Gtk.Box
        :param args:
        :return:
        """

        self.vbox.pack_start(*args, **kwargs)

        return 0

    def set_label_text(self, label):
        """
        Sets the text label of the Gtk.Frame
        :param label:
        :return:
        """
        self.set_label(label=label)

if __name__ == "__main__":

    window = Gtk.Window(title="Widgets Test Window")
    window.connect("destroy", lambda q: Gtk.main_quit())
    test_fpdf = FrontPageDeviceFrame(label="Device 1")
    window.add(test_fpdf)

    fpds = []

    for i in range(5):

        if i == 2:

            test_fpd = FrontPageDisplayValue("Channel %i" % i, "kV", displayformat=".2e", set_flag=True)

        else:

            test_fpd = FrontPageDisplayValue("Channel %i" % i, "kV")

        test_fpdf.pack_start(test_fpd, True, True, 0)
        test_fpd.set_value(i*10)
        fpds.append(test_fpd)

    print("%s: %.2f %s" % (fpds[2].get_name(), fpds[2].get_value(), fpds[2].get_unit()))

    window.show_all()
    Gtk.main()

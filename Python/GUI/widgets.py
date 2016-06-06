import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject
__author__ = "Aashish Tripathee and Daniel Winklehner"
__doc__ = """A number of widgets inheriting from gi to be placed in the GUI repeatedly"""


class FrontPageDisplayValue(Gtk.Frame):
    """
    Simple widget with two labels and a entry box to display a single value
    """

    def __init__(self, name="Channel N/A", unit="N/A", displayformat=None, set_flag=False):
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

        self.set_flag = set_flag
        self.displayformat = displayformat

        self.add(hbox)

        hbox.pack_start(self.name_label, True, True, 0)
        hbox.pack_start(self.value_entry, True, True, 0)
        hbox.pack_start(self.unit_label, True, True, 0)

        if not self.set_flag:
            self.value_entry.set_sensitive(False)

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
        if self.displayformat is None:
            self.displayformat = ".2f"

        self.value_entry.set_text("{0:{1}}".format(value, self.displayformat))

        return 0


if __name__ == "__main__":
    window = Gtk.Window(title="Widgets Test Window")
    window.connect("destroy", lambda q: Gtk.main_quit())
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    window.add(vbox)

    fpds = []

    for i in range(5):
        if i == 2:
            test_fpd = FrontPageDisplayValue("Channel %i" % i, "kV", displayformat=".2e", set_flag=True)
        else:
            test_fpd = FrontPageDisplayValue("Channel %i" % i, "kV")
        vbox.pack_start(test_fpd, True, True, 0)
        test_fpd.set_value(i*10)
        fpds.append(test_fpd)

    print("%s: %.2f %s" % (fpds[2].get_name(), fpds[2].get_value(), fpds[2].get_unit()))

    window.show_all()
    Gtk.main()

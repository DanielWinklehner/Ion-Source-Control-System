import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject
__author__ = "Aashish Tripathee and Daniel Winklehner"
__doc__ = """A number of widgets inheriting from gi to be placed in the GUI repeatedly"""


class FrontPageDisplay(Gtk.Frame):
    """
    Simple widget with two labels and a entry box to display a single value
    """

    def __init__(self, name="Channel N/A", unit="N/A"):

        Gtk.Frame.__init__(self)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.name_label = Gtk.Label(name)
        self.unit_label = Gtk.Label(unit)
        self.value_entry = Gtk.Entry()

        self.add(hbox)
        hbox.pack_start(self.name_label, True, True, 0)
        hbox.pack_start(self.value_entry, True, True, 0)
        hbox.pack_start(self.unit_label, True, True, 0)

    def get_name(self):
        """
        Returns the name label as str
        :return:
        """

        return self.name_label.get_text()

    def get_value(self):
        """
        Returns the value entries value as float
        :return:
        """

        return float(self.value_entry.get_text())

    def set_value(self, value):
        """
        Sets the value in the value entry
        :param value:
        :return:
        """
        self.value_entry.set_text(str(value))

        return 0


if __name__ == "__main__":
    window = Gtk.Window(title="Widgets Test Window")
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    window.add(vbox)

    fpds = []

    for i in range(5):
        test_fpd = FrontPageDisplay("Power Supply %i" % i, "kV")
        vbox.pack_start(test_fpd, True, True, 0)
        test_fpd.set_value(i*10)
        fpds.append(test_fpd)

    print("%s: %.5f" % (fpds[2].get_name(), fpds[2].get_value()))

    window.show_all()
    Gtk.main()

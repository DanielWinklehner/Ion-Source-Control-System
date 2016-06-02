import gi
gi.require_version('Gtk', '3.0')
import time
from gi.repository import Gtk, GLib, GObject
__author__ = "Aashish Tripathee and Daniel Winklehner"
__doc__ = """GUI without actual functionality"""


class MIST1ControlSystem:
    """
    Main class that runs the GUI for the MIST-1 control system
    """

    def __init__(self):
        """
        Initialize the control system GUI
        """
        # --- Load the GUI from XML file and initialize connections --- #
        self._builder = Gtk.Builder()
        self._builder.add_from_file("mist_control_system_main_gui.glade")
        self._builder.connect_signals(self.get_connections())

        self._main_window = self._builder.get_object("main_window")

        self._main_window.connect("destroy", Gtk.main_quit)

        # --- Get some widgets from the builder --- #
        self.status_bar = self._builder.get_object("main_statusbar")
        self.log_textbuffer = self._builder.get_object("log_texbuffer")

        # --- Show the GUI --- #
        self._main_window.maximize()
        self._main_window.show_all()

    def emergency_stop(self, widget):
        """
        Callback for STOP button, but may also be called if interlock is broken or
        in any other unforseen sircumstance that warrants shutting down all power supplies.
        :param widget:
        :return:
        """

        self.status_bar.push(1, "Emergency stop button was pushed!")

        return 0

    def get_connections(self):
        """
        This just returns a dictionary of connections
        :return:
        """
        con = {"main_quit": self.main_quit,
               "stop_button_clicked_cb": self.emergency_stop,
               "on_main_statusbar_text_pushed": self.statusbar_changed_callback
               }

        return con

    def main_quit(self, widget):
        """
        Shuts down the program (and threads) gracefully.
        :return:
        """

        self._main_window.destroy()
        Gtk.main_quit()

        return 0

    def statusbar_changed_callback(self, statusbar, context_id, text):
        """
        Callback that handles what happens when a message is pushed in the
        statusbar
        """

        timestr = time.strftime("%d %b, %Y, %H:%M:%S: ", time.localtime())

        self.log_textbuffer.insert(self.log_textbuffer.get_end_iter(), timestr + text + "\n")

        return 0


if __name__ == "__main__":
    control_system = MIST1ControlSystem()
    Gtk.main()

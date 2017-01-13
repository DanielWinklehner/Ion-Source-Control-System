# -*- coding: utf-8 -*-
"""
Dialoge classes for Venus Warp Simulations Post Processor

includes:
FileDialog
RasterInput
MetaInput
PlotSettingsInput

Daniel Winklehner, LBNL 2010
"""

# PyGObject Introspection and glade
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject


import numpy as np

import os, sys

def sorry_popup(text=None):
    if text is not None:
        md = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT, Gtk.MESSAGE_INFO, Gtk.BUTTONS_OK, text)
        md.set_title("Sorry...")
        md.run()
        md.destroy()

class SettingsDialog3:
    """
    Dialog box for all the different plot settings in the WARP postprocessor
    """
    def __init__(self):
        """
        Constructor of the SettingsDialog class
        """
        self.gladefile  = os.path.join(os.path.dirname(__file__),"PlotSettingsDialog.glade")

        # Uncomment this line for cxFreeze binary building
        #self.gladefile  = "PlotSettingsDialog.glade"

        self.Settings   = None

    def timestr(self, s):
        """
        Takes a value in seconds (s) and converts it into a string of the
        format hh:mm:ss in 24 hour time.
        If the number of seconds exceeds a day, it starts over from the
        beginning. This assumes that days is the largest unit of time in the
        context.
        """

        # Number of days (if any)
        days = int(s/86400)

        if days > 0: s = s - days*86400

        h = int(s/3600)
        m = int((s-3600*h)/60)
        s = int(s - 3600*h - 60*m)

        if h < 10: hstr = "0%i"%(h)
        else: hstr = "%i"%(h)

        if m < 10: mstr = "0%i"%(m)
        else: mstr = "%i"%(m)

        if s < 10: sstr = "0%i"%(s)
        else: sstr = "%i"%(s)

        timestr = hstr+":"+mstr+":"+sstr

        return timestr

    def generate_default_settings(self):
        """
        Generates a set of default values to use as entries in the Settings
        Dialog
        """
        entries         = { "title"         : "Title",
                            "x_label"       : "x",
                            "y1_label"      : "y",
                            "y2_label"      : "secondary y",
                            "x_min"         : float(-1),
                            "y1_min"        : float(-1),
                            "y2_min"        : float(-1),
                            "x_max"         : float(1),
                            "y1_max"        : float(1),
                            "y1_max"        : float(1)}

        adjustments     = { "major_ticks"   : 15,
                            "label_fs"      : 30,
                            "legend_ms"     : 1,
                            "legend_fs"     : 18,
                            "legend_lw"     : 1,
                            "title_fs"      : 30,
                            "line_width"    : 1,
                            "marker_size"   : 25
                           }

        legend          = []

        defaults = {"entry":                entries,
                    "adj":                  adjustments,
                    "legend_entries":       legend,
                    "legend_global_flag":   False,
                    "legend_entries_flags": np.array([], 'bool'),
                    "autoscalex":           True,
                    "autoscaley1":          True,
                    "autoscaley2":          True,
                    "xtime":                False}

        return defaults

    def add_legend_entry(self, table, row, entry = "", l_ms = 1, l_lw = 1, l_flag = True):
        """
        TODO?
        """

        return 0

    def deactivate_autoscale_x(self, entry):
        """
        """

        self.wTree.get_object("autoscalex_cb").set_active(False)

        return 0

    def deactivate_autoscale_y(self, entry):
        """
        """

        self.wTree.get_object("autoscaley1_cb").set_active(False)

        return 0

    def deactivate_secondary_autoscale_y(self, entry):
        """
        """

        self.wTree.get_object("autoscaley2_cb").set_active(False)

        return 0

    def run(self, parent=None, old_settings=None):
        """
        Function that shows the dialog and gives back the dict with all the
        new settings
        """
        if old_settings is None:

            old_settings = self.generate_default_settings()

        self.Settings = old_settings.copy()

        # --- Generate Dialog GUI from gladefile --- #
        self.wTree = Gtk.Builder()
        self.wTree.add_from_file(self.gladefile)
        self.dialog = self.wTree.get_object("settings_dialog")

        if parent is not None:
            self.dialog.set_transient_for(parent)

        self.wTree.connect_signals({"deactivate_autoscale_x": self.deactivate_autoscale_x,
                                    "deactivate_autoscale_y1": self.deactivate_autoscale_y,
                                    "deactivate_autoscale_y2": self.deactivate_secondary_autoscale_y})

        # --- Fill in the entries and spinboxes with the current values --- #
        for key in old_settings["entry"].keys():

            self.wTree.get_object(key+"_entry").set_text(str(old_settings["entry"][key]))

        for key in old_settings["adj"].keys():

            self.wTree.get_object(key+"_adj").set_value(old_settings["adj"][key])

        # --- Make a VBox for the legend entries --- #
        legend_table = self.wTree.get_object("legend_table")

        legend_entries = []
        legend_entry_show = []

        old_legend = self.Settings["legend_entries"]
        old_legend_flags = self.Settings["legend_entries_flags"]

        n_legend_entries = len(old_legend)

        legend_table.resize(n_legend_entries+1, 4)

        for i in range(len(old_legend)):

            l_entry = Gtk.Entry()
            l_flag_cb = Gtk.CheckButton()
            l_flag_cb.set_active(old_legend_flags[i])
            l_flag_cb.show()
            #l_flag_cb.set_sensitive(False)
            l_entry.set_size_request(300,-1)
            l_entry.set_text(old_legend[i])
##            l_entry.set_activates_default(True)

            legend_entries.append(l_entry)
            legend_entry_show.append(l_flag_cb)

            legend_table.attach(l_entry, 0,1,i+1,i+2)
            legend_table.attach(l_flag_cb, 1,2,i+1,i+2)

        legend_table.show_all()

        if old_settings["legend_global_flag"]: self.wTree.get_object("legend_cb").set_active(True)
        if old_settings["autoscalex"]: self.wTree.get_object("autoscalex_cb").set_active(True)
        if old_settings["autoscaley1"]: self.wTree.get_object("autoscaley1_cb").set_active(True)
        if old_settings["autoscaley2"]: self.wTree.get_object("autoscaley2_cb").set_active(True)

        if old_settings["xtime"]:

            self.wTree.get_object("x_min_entry").set_text(self.timestr(float(self.wTree.get_object("x_min_entry").get_text())))
            self.wTree.get_object("x_max_entry").set_text(self.timestr(float(self.wTree.get_object("x_max_entry").get_text())))

        response = self.dialog.run()

        if response == 1:

            for key in old_settings["entry"].keys():

                if key in ["title", "x_label", "y1_label", "y2_label"]:

                    self.Settings["entry"][key] = self.wTree.get_object(key+"_entry").get_text()

                else:

                    text = self.wTree.get_object(key+"_entry").get_text()

                    if old_settings["xtime"]:

                        if key in ["x_min", "x_max"]:

                            try:

                                h,m,s = text.split(":")
                                self.Settings["entry"][key] = int(h) * 3600 + int(m) * 60 + float(s)

                            except:

                                return -1, None

                        else:

                            if text == "": text = "0.0"
                            self.Settings["entry"][key] = float(text)

                    else:

                        if text == "": text = "0.0"
                        self.Settings["entry"][key] = float(text)

            for key in old_settings["adj"].keys():

                self.Settings["adj"][key] = self.wTree.get_object(key+"_adj").get_value()

            if self.wTree.get_object("legend_cb").get_active(): self.Settings["legend_global_flag"] = True
            else: self.Settings["legend_global_flag"] = False
            if self.wTree.get_object("autoscalex_cb").get_active(): self.Settings["autoscalex"] = True
            else: self.Settings["autoscalex"] = False
            if self.wTree.get_object("autoscaley1_cb").get_active(): self.Settings["autoscaley1"] = True
            else: self.Settings["autoscaley1"] = False
            if self.wTree.get_object("autoscaley2_cb").get_active(): self.Settings["autoscaley2"] = True
            else: self.Settings["autoscaley2"] = False

            for i in range(len(legend_entries)):

                self.Settings["legend_entries"][i] = legend_entries[i].get_text()
                self.Settings["legend_entries_flags"][i] = legend_entry_show[i].get_active()

            self.dialog.destroy()

            return response, self.Settings

        else:

            self.dialog.destroy()

            return response, None


class MetaInput3(object):
    """
    A Dialog Box for Single Line Input
    """
    def __init__(self):
        self.input_line = None
        self.dialog = Gtk.Dialog("", None, Gtk.DIALOG_DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_OK, Gtk.RESPONSE_OK, Gtk.STOCK_CANCEL, Gtk.RESPONSE_CANCEL))
        self.inpBox = Gtk.Entry()
        self.inpBox.set_size_request(250,30)
        self.inpBox.set_activates_default(True)
        self.inpBox.show()
        self.dialog.vbox.pack_start(self.inpBox, True, True,4)
        self.dialog.set_default_response(Gtk.RESPONSE_OK)

    def get_input(self, Title):
        self.dialog.set_title(Title)
        response = self.dialog.run()
        input_line=self.inpBox.get_text()
        self.dialog.destroy()

        if response == Gtk.RESPONSE_OK:
            self.input_line = input_line
            return input_line
        else:
            return None

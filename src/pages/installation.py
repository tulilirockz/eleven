from tempfile import mkstemp
import threading

import subprocess
import gi
import time

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GObject, Gio, Gtk, Gdk


@Gtk.Template(resource_path="/dev/getapollo/Eleven/installation.ui")
class ElevenInstallationPage(Adw.Bin):
    __gtype_name__ = "ElevenInstallationPage"
    __gsignals__ = {
        "proceed-success-installation-page": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (str,),
        ),
        "proceed-failure-installation-page": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (str,),
        ),
    }

    status_page: Adw.StatusPage = Gtk.Template.Child()
    terminal_box: Gtk.Box = Gtk.Template.Child()
    terminal_output: Gtk.TextView = Gtk.Template.Child()
    temporary_file = mkstemp("eleven-installer")[1]
    temp_file_gio = Gio.File.new_for_uri(f"file://{temporary_file}")
    temp_file_monitor = temp_file_gio.monitor(Gio.FileMonitorFlags.NONE, None)
    running_installation = True

    def do_copy_clipboard_termnal(self, button: Gtk.Button):
        display = Gdk.Display.get_default()
        if display == None:
            return
        clipboard = display.get_clipboard()

        terminal_buffer = self.terminal_output.get_buffer()
        terminal_buffer.select_range(
            terminal_buffer.get_start_iter(), terminal_buffer.get_end_iter()
        )
        terminal_buffer.copy_clipboard(clipboard)

    @Gtk.Template.Callback()
    def do_show_terminal(self, button: Gtk.ToggleButton):
        self.status_page.set_visible(not button.get_active())
        self.terminal_box.set_visible(button.get_active())

    def start_installation(self):
        print("tarting")
        self.installation_thread = threading.Thread(
            target=self.run_installation_thread
        )
        GObject.timeout_add(1000, self.update_progress)
        self.installation_thread.start()

    def run_installation_thread(self):
        self.successful_run = False
        self.successful_run = install_bootc_to_device("", self.temporary_file)
        time.sleep(10)
        GObject.idle_add(self.stop_installation)

    def update_progress(self):
        if self.running_installation:
            print("uhh running")
        if not self.running_installation:
            print("uhh not running")
        return self.running_installation

    def stop_installation(self):
        self.running_installation = False
        if self.successful_run:
            self.emit("proceed-success-installation-page", "")
        else:
            self.emit("proceed-failure-installation-page", "")
        self.installation_thread.join()

    def on_logfile_changed(self, _file, _other_file, idk, event):
        if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            # FIXME: this is a really dumb way of implementing this, please figure out some better way
            with open(self.temporary_file, "r") as tmpfileall:
                self.terminal_output.get_buffer().set_text(tmpfileall.read())
            return

    def __init__(self, service, **kwargs):
        super().__init__(**kwargs)

        self.service = service

        # FIXME: utilize `LOGO` variable on `/etc/os-release` as the base
        print(self.temporary_file)
        self.temp_file_monitor.connect("changed", self.on_logfile_changed)

        buffer = self.terminal_output.get_buffer()
        buffer.set_text("amogus")

        self.status_page.set_title(
            str(self.status_page.get_title()).format(
                os_name=self.service.config.os_name
            )
        )


# monolithic function that partitions and installs a selected image to a target device, WILL automatically wipe everything as this is supposed to be an internal function
def install_bootc_to_device(target_path: str, logfile_path: str) -> bool:
    # with open(logfile_path, "w") as logfile:
    #     subprocess.run(["systemd-repart", "--dry-run=no", "--empty=allow", "--no-pager", "--pretty=false", "--no-legend", "--definitions=${ZINST_REPART_DIR}", target_path], stdout=logfile, stderr=logfile)
    #     subprocess.run(["systemd-repart", "--dry-run=yes", "--empty=allow", "--no-pager", "--pretty=false", "--no-legend", "--definitions=${ZINST_REPART_DIR}", target_path, "--json=short"], stdout=logfile, stderr=logfile)
    return False

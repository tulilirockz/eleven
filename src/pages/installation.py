from tempfile import mkstemp
import threading

import subprocess
from typing import Any
from pathlib import Path
import gi
import json
from tempfile import mkdtemp

from gi.repository.GLib import mkdir_with_parents

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
        try:
            self.successful_run = install_bootc_to_device(
                self.service.config.repart_path,
                self.service.config.target_device_to_install,
                self.temporary_file,
                self.service.config.target_imgref,
                self.service.config.source_imgref,
            )
        except Exception as e:
            self.successful_run = False
            print(e)
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
def install_bootc_to_device(
    repart_path: str,
    target_path: str,
    logfile_path: str,
    target_imgref: str,
    source_imgref: str,
) -> bool:
    with open(logfile_path, "w") as logfile:
        print(
            "running command",
            [
                "systemd-repart",
                "--dry-run=no",
                "--empty=allow",
                "--no-pager",
                "--pretty=false",
                "--no-legend",
                f"--definitions={repart_path}",
                target_path,
                "--json=short",
            ],
        )

        repart_out = subprocess.run(
            [
                "pkexec",
                "systemd-repart",
                "--dry-run=no",
                "--empty=force",
                "--no-pager",
                "--pretty=false",
                "--no-legend",
                f"--definitions={repart_path}",
                target_path,
                "--json=short",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.decode("utf-8")
        logfile.write(str(repart_out))
        partition_out: dict[Any, Any] = json.loads(repart_out)
        print(partition_out)

        root_partition_path: str = list(
            filter(
                lambda x: x if x["type"].startswith("root") else None,
                partition_out,
            )
        )[0]["node"]
        boot_partition_path: str = list(
            filter(
                lambda x: x if x["type"] == "xbootldr" else None,
                partition_out,
            )
        )[0]["node"]
        esp_partition_path: str = list(
            filter(
                lambda x: x if x["type"] == "esp" else None,
                partition_out,
            )
        )[0]["node"]
        print(root_partition_path)
        print(boot_partition_path)
        print(esp_partition_path)

        if root_partition_path == "":
            print("Failed finding root partition for disk")
            return False

        root_mount_dir = mkdtemp("eleven-installer")
        subprocess.run(
            [
                "pkexec",
                "mount",
                "-t",
                "auto",
                root_partition_path,
                root_mount_dir,
            ],
            stdout=logfile,
            stderr=logfile,
        )

        subprocess.run(
            ["pkexec", "mkdir", "-p", f"{root_mount_dir}/boot"],
            stdout=logfile,
            stderr=logfile,
        )

        subprocess.run(
            [
                "pkexec",
                "mount",
                "-t",
                "auto",
                boot_partition_path,
                f"{root_mount_dir}/boot",
            ],
            stdout=logfile,
            stderr=logfile,
        )

        subprocess.run(
            ["pkexec", "mkdir", "-p", f"{root_mount_dir}/boot/efi"],
            stdout=logfile,
            stderr=logfile,
        )

        subprocess.run(
            [
                "pkexec",
                "mount",
                "-t",
                "auto",
                esp_partition_path,
                f"{root_mount_dir}/boot/efi",
            ],
            stdout=logfile,
            stderr=logfile,
        )

        subprocess.run(
            [
                "pkexec",
                "bootc",
                "install",
                "to-filesystem",
                "--acknowledge-destructive",
                "--target-imgref",
                target_imgref,
                "--enforce-container-sigpolicy",
                "--skip-fetch-check",
                "--source-imgref",
                source_imgref,
                root_mount_dir,
            ],
            stdout=logfile,
            stderr=logfile,
        )

    # trap 'umount ${ROOT_MOUNT} ; umount ${ROOT_MOUNT}/boot ; umount ${ROOT_MOUNT}/boot/efi' EXIT

    return True

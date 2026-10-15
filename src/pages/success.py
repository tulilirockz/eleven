import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk


@Gtk.Template(resource_path="/dev/getapollo/Eleven/success.ui")
class ElevenSuccessPage(Adw.Bin):
    __gtype_name__ = "ElevenSuccessPage"

    status_page: Adw.StatusPage = Gtk.Template.Child()

    def __init__(self, service, **kwargs):
        super().__init__(**kwargs)

        self.service = service

        self.status_page.set_title(
            str(self.status_page.get_title()).format(
                os_name=self.service.config.os_name
            )
        )

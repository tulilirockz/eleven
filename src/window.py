from gi.repository import Adw
from gi.repository import Gtk

from .welcome import ElevenWelcomePage
from .disks import ElevenDisksPage
from .experimental import ElevenExperimentalPage
from .installation import ElevenInstallationPage

from .success import ElevenSuccessPage
from .failure import ElevenFailurePage

from gettext import gettext as _


@Gtk.Template(resource_path="/dev/getapollo/Eleven/window.ui")
class ElevenWindow(Adw.ApplicationWindow):
    __gtype_name__ = "ElevenWindow"

    welcome_view: Adw.NavigationPage = Gtk.Template.Child()
    disks_view: Adw.NavigationPage = Gtk.Template.Child()
    installation_view: Adw.NavigationPage = Gtk.Template.Child()
    success_view: Adw.NavigationPage = Gtk.Template.Child()
    failure_view: Adw.NavigationPage = Gtk.Template.Child()
    stack: Adw.NavigationView = Gtk.Template.Child()

    def __init__(self, service, **kwargs):
        super().__init__(**kwargs)

        self.service = service

        self.welcome_page: ElevenWelcomePage = ElevenWelcomePage(self.service)
        self.disks_page: ElevenDisksPage = ElevenDisksPage(self.service)
        self.installation_page: ElevenInstallationPage = ElevenInstallationPage(
            self.service
        )
        self.success_page: ElevenSuccessPage = ElevenSuccessPage(self.service)
        self.failure_page: ElevenFailurePage = ElevenFailurePage(self.service)
        self.installation_page: ElevenInstallationPage = ElevenInstallationPage(
            self.service
        )

        self.success_view.set_child(self.success_page)
        self.failure_view.set_child(self.failure_page)
        self.installation_view.set_child(self.installation_page)
        self.installation_page: ElevenInstallationPage = ElevenInstallationPage(
            self.service
        )

        self.welcome_view.set_child(self.welcome_page)
        self.disks_view.set_child(self.disks_page)

        self.installation_page.connect(
            "proceed-success-installation-page", self.show_success_view
        )
        self.installation_page.connect(
            "proceed-failure-installation-page", self.show_failure_view
        )

        self.disks_page.connect(
            "proceed-disks-page", self.show_installation_view
        )

        if service.config.experimental:
            self.experimental_view = Adw.NavigationPage()
            self.experimental_view.set_title(_("Experimental Software"))
            self.experimental_page = ElevenExperimentalPage(self.service)
            self.experimental_view.set_child(self.experimental_page)

            self.experimental_page.proceed_button.connect(
                "clicked", self.acknowledge_experimental_warning
            )

            self.stack.replace(
                [
                    self.experimental_view,
                ]
            )

            self.stack.pop_to_page(self.experimental_view)

        self.welcome_page.try_btn.connect("clicked", self.try_os)
        self.welcome_page.install_btn.connect("clicked", self.show_disks_view)

    def try_os(self, _button):
        self.close()

    def acknowledge_experimental_warning(self, _button):
        self.stack.push(self.welcome_view)

    def show_disks_view(self, _button):
        self.stack.push(self.disks_view)

    def show_installation_view(self, _view, _something):
        self.installation_page.start_installation()

        self.stack.replace(
            [
                self.installation_view,
            ]
        )
        self.stack.pop_to_page(self.installation_view)

    def show_success_view(self, _view, _something):
        self.stack.replace(
            [
                self.success_view,
            ]
        )
        self.stack.pop_to_page(self.success_view)

    def show_failure_view(self, _view, _something):
        self.stack.replace(
            [
                self.failure_view,
            ]
        )
        self.stack.pop_to_page(self.failure_view)

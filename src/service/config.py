from pathlib import Path
import tomllib

from gettext import gettext as _


class ElevenInstallerServiceConfig:
    config_path = Path("/usr/share/apollo/eleven/config.toml")
    repart_path = Path("/usr/share/apollo/eleven/repart.d")

    # Storing this information here so we can format/install to the disk later
    target_device_to_install = ""

    def __init__(self, *kwargs, log):
        self.log = log

        self.exists = False
        self.valid = False

        # make sure certain values are set
        self.os_name = ""
        self.experimental = False

    def load_config(self, *kwargs):
        with open("/usr/share/apollo/eleven/config.toml", "rb") as config:
            # Required/mandatory values
            try:
                data = tomllib.load(config)

                self.os_name = data["info"]["os_name"]

                self.filesystem = data["disks"]["filesystem"]
                self.efi_size = data["disks"]["efi_size"]

                self.target_imgref = data["bootc"]["target_imgref"]
                self.source_imgref = data["bootc"]["source_imgref"]

            except KeyError as e:
                self.log.new_entry(
                    3,
                    _(
                        "Configuration has missing parameter: {parameter}"
                    ).format(parameter=e),
                    12,
                )

                return False

            # Optional/non-required values
            self.use_composefs = data["bootc"]["use_composefs"]
            self.experimental = data["info"]["experimental"]
            self.valid = True
            return True

    def check_config_exists(self, *kwargs) -> bool:
        self.log.new_entry(1, "Checking that the configuration is present", 0)

        if self.config_path.exists():
            self.log.new_entry(1, "Configuration is present", 0)
            self.exists = True
            return True
        else:
            self.log.new_entry(
                3,
                "Configuration could not be found at /usr/share/apollo/eleven/config.toml}",
                11,
            )
            return False

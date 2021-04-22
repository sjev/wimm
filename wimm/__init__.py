from pathlib import Path
import os
import sys
import yaml
import wimm.structure as structure


__version__ = "DEV.0.0.9"

DATE_FMT = "%Y-%m-%d"


this = sys.modules[__name__]  # way to add module-wide variables


def get_path():
    """ get path of database directory """

    val = os.getenv('WIMM_PATH')

    if not val:
        return None
    return Path(val)


def get_settings():
    """ get settings from file or defaults """

    path = get_path()

    if path is None:
        return structure.settings

    p = path / structure.files['settings']
    assert p.exists(), f'no settings file in {p.as_posix()}'

    settings = yaml.load(p.open(), Loader=yaml.SafeLoader)
    settings['path'] = path

    return settings

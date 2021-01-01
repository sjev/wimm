__version__ = "DEV.0.0.2"

DATE_FMT = "%Y-%m-%d"

import sys
import os
from pathlib import Path

this = sys.modules[__name__] # way to add module-wide variables

def get_path():
    """ get path of database directory """
    
    val = os.getenv('WIMM_PATH')

    if not val:
        return None
    return Path(val)

this.config = {'path': get_path() }

def get_settings():
    """ get settings from file or defaults """
    
    import wimm.structure as structure
    path = this.config['path']
    
    if path is None:
        return structure.settings
    
    p = path / structure.files['settings']
    if p.exists():
        import yaml
        settings = yaml.load(p.open(), Loader=yaml.SafeLoader)
        return settings
    else:
        return structure.settings
        
    
    
this.config = {**this.config, **get_settings()}
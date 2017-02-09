import os
import envdir

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promgen.settings')
os.environ.setdefault('CONFIG_DIR', os.path.expanduser('~/.config/promgen'))
default_app_config = 'promgen.apps.PromgenConfig'

if os.path.exists(os.environ['CONFIG_DIR']):
    envdir.open(os.environ['CONFIG_DIR'])

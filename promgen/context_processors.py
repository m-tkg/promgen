# Copyright (c) 2017 LINE Corporation
# These sources are released under the terms of the MIT license: see LICENSE

from django.conf import settings

from promgen.models import FARM_DEFAULT
from promgen.version import __version__


def settings_in_view(request):
    return {
        'FARM_DEFAULT': FARM_DEFAULT,
        'EXTERNAL_LINKS': settings.PROMGEN.get('links', {}),
        'VERSION': __version__,
    }

"""
Plugin definition for the overview Opal plugin
"""
from opal.core import plugins

from overview.urls import urlpatterns


class OverviewPlugin(plugins.OpalPlugin):
    """
    Main entrypoint to expose this plugin to our Opal application.
    """
    urls = urlpatterns
    javascripts = {
        # Add your javascripts here!
        'opal.overview': [
            # 'js/overview/app.js',
            # 'js/overview/controllers/larry.js',
            # 'js/overview/services/larry.js',
        ]
    }

    def list_schemas(self):
        """
        Return any patient list schemas that our plugin may define.
        """
        return {}

    def roles(self, user):
        """
        Given a (Django) USER object, return any extra roles defined
        by our plugin.
        """
        return {}

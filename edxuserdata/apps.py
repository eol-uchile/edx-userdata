from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import (
    PluginSettings,
    PluginURLs,
    ProjectType,
    SettingsType,
)


class EdxUserDataConfig(AppConfig):
    name = 'edxuserdata'
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: "edxuserdata-data",
                PluginURLs.REGEX: r"^edxuserdata/",
                PluginURLs.RELATIVE_PATH: "urls",
            }}
    }

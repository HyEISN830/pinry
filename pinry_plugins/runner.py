import logging

from django.conf import settings
from django.utils.module_loading import import_string

_plugin_instances = None


def _load_plugins():
    instances = []
    for plugin_path in getattr(settings, "ENABLED_PLUGINS", []):
        try:
            plugin_cls = import_string(plugin_path)
            instances.append(plugin_cls())
        except Exception:
            logging.exception("Error loading pinry plugin %s", plugin_path)
    return instances


def get_plugin_instances():
    global _plugin_instances
    if _plugin_instances is None:
        _plugin_instances = _load_plugins()
    return _plugin_instances


def run_image_pre_creation(image_instance):
    for plugin in get_plugin_instances():
        process_fn = getattr(plugin, "process_image_pre_creation", None)
        if process_fn is None:
            continue
        try:
            process_fn(
                django_settings=settings,
                image_instance=image_instance,
            )
        except Exception:
            logging.exception(
                "Error occurs while trying to access plugin's pin_pre_save "
                "for plugin %s",
                plugin,
            )


def run_thumbnail_pre_creation(thumbnail_instance):
    for plugin in get_plugin_instances():
        process_fn = getattr(plugin, "process_thumbnail_pre_creation", None)
        if process_fn is None:
            continue
        try:
            process_fn(
                django_settings=settings,
                thumbnail_instance=thumbnail_instance,
            )
        except Exception:
            logging.exception(
                "Error occurs while trying to access plugin's process_thumbnail_pre_creation "
                "for plugin %s",
                plugin,
            )

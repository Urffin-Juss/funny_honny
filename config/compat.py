import sys

import django


def apply_python314_django_context_patch() -> None:
    """Patch Django 5.1 context copy bug on Python 3.14.

    Django 5.1.x uses `copy(super())` in BaseContext.__copy__, which breaks on
    Python 3.14 during admin template rendering.
    """
    if sys.version_info < (3, 14):
        return
    if not django.get_version().startswith("5.1"):
        return

    from django.template.context import BaseContext

    def _safe_copy(self):
        duplicate = object.__new__(self.__class__)
        duplicate.__dict__ = self.__dict__.copy()
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _safe_copy

"""
Compile .po to .mo using Babel (no gettext required).
Run: python manage.py compilemessages_python
"""
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Compile locale .po files to .mo using Babel (for systems without gettext)"

    def handle(self, *args, **options):
        try:
            from babel.messages.mofile import write_mo
            from babel.messages.pofile import read_po
        except ImportError:
            self.stderr.write(
                "Install Babel: pip install Babel"
            )
            return

        base_dir = Path(settings.BASE_DIR)
        locale_dirs = getattr(settings, "LOCALE_PATHS", []) or []
        if not locale_dirs:
            locale_dirs = [base_dir / "locale"]
        else:
            locale_dirs = [Path(d) for d in locale_dirs]

        compiled = 0
        for locale_dir in locale_dirs:
            if not locale_dir.exists():
                continue
            for lang_dir in locale_dir.iterdir():
                if not lang_dir.is_dir():
                    continue
                lc_messages = lang_dir / "LC_MESSAGES"
                po_file = lc_messages / "django.po"
                mo_file = lc_messages / "django.mo"
                if not po_file.exists():
                    continue
                try:
                    with open(po_file, "rb") as f:
                        catalog = read_po(f)
                    with open(mo_file, "wb") as f:
                        write_mo(f, catalog)
                    self.stdout.write(self.style.SUCCESS(f"Compiled {po_file} -> {mo_file}"))
                    compiled += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error compiling {po_file}: {e}"))

        if compiled:
            self.stdout.write(self.style.SUCCESS(f"Done. Compiled {compiled} message catalog(s)."))
        else:
            self.stdout.write("No .po files found in LOCALE_PATHS.")

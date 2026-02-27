import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from members.models import Member
from django.forms.models import model_to_dict

qs = Member.objects.all()
print("COUNT:", qs.count())

data = []

for m in qs:
    d = model_to_dict(m)
    clean_dict = {}

    for key, value in d.items():
        if hasattr(value, "isoformat"):
            clean_dict[key] = value.isoformat()
        else:
            clean_dict[key] = value

    if m.photo:
        clean_dict["photo"] = m.photo.name
    else:
        clean_dict["photo"] = None

    data.append(clean_dict)

print("Final length:", len(data))

with open("safe_members.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("EXPORT SUCCESS")
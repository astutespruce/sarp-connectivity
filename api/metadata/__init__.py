from datetime import date
import json
from pathlib import Path


from api.constants import DAM_FIELD_DEFINITIONS, SB_FIELD_DEFINITIONS

working_dir = Path(__file__).resolve().parent


with open(working_dir.parent.parent / "ui/package.json") as infile:
    info = json.loads(infile.read())
    data_version = info["version"]
    data_date = info["date"]

with open(working_dir / "description.txt") as infile:
    description = infile.read()

with open(working_dir / "terms_of_use.txt") as infile:
    terms_of_use = infile.read()


with open(working_dir / "readme_template.txt") as infile:
    readme = infile.read()

with open(working_dir / "terms_template.txt") as infile:
    terms = infile.read()


def get_readme(filename, barrier_type, fields, url, layer, ids):
    field_def = (
        DAM_FIELD_DEFINITIONS if barrier_type == "dams" else SB_FIELD_DEFINITIONS
    )

    fields = {f: field_def[f] for f in fields if f in fields}
    field_info = "\n".join([f"{k}: {v}" for k, v in fields.items()])

    return readme.format(
        type=barrier_type,
        download_date=date.today().strftime("%m/%d/%Y"),
        data_version=data_version,
        data_date=data_date,
        url=url,
        filename=filename,
        layer=layer,
        ids=", ".join(ids),
        description=description,
        field_info=field_info,
    )


def get_terms(url):
    return terms.format(
        download_date=date.today().strftime("%m/%d/%Y"),
        data_version=data_version,
        data_date=data_date,
        url=url,
        year=date.today().year,
        terms_of_use=terms_of_use,
    )
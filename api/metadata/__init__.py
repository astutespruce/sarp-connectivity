from datetime import date
from pathlib import Path

from api.settings import data_version, data_date


from api.constants import DAM_FIELD_DEFINITIONS, SB_FIELD_DEFINITIONS

metadata_dir = Path(__file__).resolve().parent

with open(metadata_dir / "description.txt") as infile:
    description = infile.read()

with open(metadata_dir / "terms_of_use.txt") as infile:
    terms_of_use = infile.read()

with open(metadata_dir / "readme_template.txt") as infile:
    readme = infile.read()

with open(metadata_dir / "terms_template.txt") as infile:
    terms = infile.read()


def get_readme(filename, barrier_type, fields, url, layer, ids):
    field_def = (
        DAM_FIELD_DEFINITIONS if barrier_type == "dams" else SB_FIELD_DEFINITIONS
    )

    fields = {f: field_def[f] for f in fields if f in fields}
    field_info = "\n".join([f"{k}: {v}" for k, v in fields.items()])

    return readme.format(
        type=barrier_type,
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
        data_version=data_version,
        data_date=data_date,
        url=url,
        year=date.today().year,
        terms_of_use=terms_of_use,
    )

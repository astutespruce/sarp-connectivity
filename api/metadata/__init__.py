from datetime import date
from pathlib import Path

from api.settings import DATA_VERSION, DATA_DATE, SITE_URL, CONTACT_EMAIL


from api.constants import (
    DAM_FIELD_DEFINITIONS,
    SB_FIELD_DEFINITIONS,
    COMBINED_FIELD_DEFINITIONS,
    ROAD_CROSSING_FIELD_DEFINITIONS,
)

metadata_dir = Path(__file__).resolve().parent

with open(metadata_dir / "description.txt") as infile:
    description = infile.read().format(contact_email=CONTACT_EMAIL)

with open(metadata_dir / "terms_of_use.txt") as infile:
    terms_of_use = infile.read()

with open(metadata_dir / "readme_template.txt") as infile:
    readme = infile.read()

with open(metadata_dir / "terms_template.txt") as infile:
    terms = infile.read()


def get_readme(filename, barrier_type, fields, unit_ids, warnings=None):
    field_def = {}
    barrier_type_label = ""

    match barrier_type:
        case "dams":
            field_def = DAM_FIELD_DEFINITIONS
            barrier_type_label = "dams"
        case "small_barriers":
            field_def = SB_FIELD_DEFINITIONS
            barrier_type_label = "surveyed road/stream crossings"
        case "combined_barriers":
            field_def = COMBINED_FIELD_DEFINITIONS
            barrier_type_label = "dams & surveyed road/stream crossings"
        case "road_crossings":
            field_def = ROAD_CROSSING_FIELD_DEFINITIONS
            barrier_type_label = "road/stream crossings"

    fields = {f: field_def[f] for f in fields if f in field_def}
    field_info = "\n".join([f"{k}: {v}" for k, v in fields.items()])

    meta_description = description if not warnings else f"{description}\n\nWARNING: {warnings}"

    return readme.format(
        type=barrier_type_label,
        data_version=DATA_VERSION,
        data_date=DATA_DATE,
        filename=filename,
        unit_ids="\n".join([f"{key}: {', '.join(ids.tolist())}" for key, ids in unit_ids.items()]),
        description=meta_description,
        field_info=field_info,
        url=SITE_URL,
        date=date.today().strftime("%m/%d/%Y"),
    )


def get_terms():
    return terms.format(
        data_version=DATA_VERSION,
        data_date=DATA_DATE,
        year=date.today().year,
        terms_of_use=terms_of_use,
        date=date.today().strftime("%m/%d/%Y"),
        url=SITE_URL,
        contact_email=CONTACT_EMAIL,
    )

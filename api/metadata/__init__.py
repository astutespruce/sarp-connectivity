from datetime import date
from pathlib import Path

from api.settings import data_version, data_date


from api.constants import (
    DAM_FIELD_DEFINITIONS,
    SB_FIELD_DEFINITIONS,
    COMBINED_FIELD_DEFINITIONS,
    ROAD_CROSSING_FIELD_DEFINITIONS,
)

metadata_dir = Path(__file__).resolve().parent

with open(metadata_dir / "description.txt") as infile:
    description = infile.read()

with open(metadata_dir / "terms_of_use.txt") as infile:
    terms_of_use = infile.read()

with open(metadata_dir / "readme_template.txt") as infile:
    readme = infile.read()

with open(metadata_dir / "terms_template.txt") as infile:
    terms = infile.read()


def get_readme(filename, barrier_type, fields, url, unit_ids, warnings=None):
    field_def = {}
    barrier_type_label = ""

    match barrier_type:
        case "dams":
            field_def = DAM_FIELD_DEFINITIONS
            barrier_type_label = "dams"
        case "small_barriers":
            field_def = SB_FIELD_DEFINITIONS
            barrier_type_label = "assessed road-related barriers"
        case "combined_barriers":
            field_def = COMBINED_FIELD_DEFINITIONS
            barrier_type_label = "dams and assessed road-related barriers"
        case "road_crossings":
            field_def = ROAD_CROSSING_FIELD_DEFINITIONS
            barrier_type_label = "road/stream crossings (potential barriers)"

    fields = {f: field_def[f] for f in fields if f in field_def}
    field_info = "\n".join([f"{k}: {v}" for k, v in fields.items()])

    meta_description = description if not warnings else f"{description}\n\nWARNING: {warnings}"

    return readme.format(
        type=barrier_type_label,
        data_version=data_version,
        data_date=data_date,
        url=url,
        filename=filename,
        unit_ids="\n".join([f"{key}: {', '.join(ids.tolist())}" for key, ids in unit_ids.items()]),
        description=meta_description,
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

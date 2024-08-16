from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import FileResponse
import pyarrow as pa
import pyarrow.compute as pc

from api.constants import (
    CoreBarrierTypes,
    BarrierTypes,
    Scenarios,
    Formats,
    CUSTOM_TIER_FIELDS,
    DAM_EXPORT_FIELDS,
    SB_EXPORT_FIELDS,
    COMBINED_EXPORT_FIELDS,
    ROAD_CROSSING_EXPORT_FIELDS,
    LOGO_PATH,
)
from api.data import data_dir
from api.lib.domains import unpack_domains
from api.lib.tiers import calculate_tiers
from api.logger import log, log_request
from api.dependencies import RecordExtractor
from api.metadata import get_readme, get_terms
from api.response import zip_csv_response


MAX_CROSSINGS = 1e6  # limit to 1M crossings in downloads


router = APIRouter()


@router.get("/{barrier_type}/{format}/national")
async def download_national(
    request: Request,
    barrier_type: CoreBarrierTypes,
    format: Formats = "csv",
):
    log_request(request)

    filename = data_dir / f"downloads/{barrier_type}.zip"

    if format == "csv":
        return FileResponse(
            filename,
            media_type="application/zip",
            # headers={"Content-Disposition": "attachment"},
            filename="aquatic_barrier_ranks.zip",
        )

    raise NotImplementedError("Other formats not yet supported")


@router.get("/{barrier_type}/{format}")
async def download(
    request: Request,
    barrier_type: BarrierTypes,
    format: Formats = "csv",
    extractor: RecordExtractor = Depends(),
    custom: bool = False,
    include_unranked=False,
    sort: Scenarios = "NCWC",
):
    """Download subset of barrier_type data.

    If `include_unranked` is `True`, all barriers in the summary units are downloaded.

    Path parameters:
    <format> : "csv"

    Query parameters:
    * one more more ids (comma delimited) for each of the unit types, e.g., State=OR,WA
    * custom: bool (default: False); set to true to perform custom ranking of subset defined here
    * include_unranked: bool (default: False); set to true to include unranked barriers in output
    * sort: str, one of 'NC', 'WC', 'NCWC'
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    columns = ["id"]
    match barrier_type:
        case "dams":
            columns += DAM_EXPORT_FIELDS
        case "small_barriers":
            columns += SB_EXPORT_FIELDS
        case "combined_barriers" | "largefish_barriers" | "smallfish_barriers":
            columns += COMBINED_EXPORT_FIELDS
        case "road_crossings":
            columns += ROAD_CROSSING_EXPORT_FIELDS

    columns = [c for c in columns if c not in CUSTOM_TIER_FIELDS]

    df = extractor.extract(
        columns=columns,
        ranked=not (include_unranked or barrier_type == "road_crossings"),
    )
    log.info(f"selected {len(df):,} {barrier_type.replace('_', ' ')} for download")

    warnings = None

    if len(df) > 0:
        if barrier_type == "road_crossings":
            if len(df) > MAX_CROSSINGS:
                log.warn("too many items requested")
                raise HTTPException(status_code=400, detail="Too many items requested")

            warnings = "this dataset includes road/stream crossings (potential barriers) derived\nfrom the USGS Road Crossings dataset (2022) or USFS National Road / Stream crossings dataset (2024)\nthat have not yet been assessed for impacts to aquatic organisms.  Unsurveyed\ncrossings are limited to those that were snapped to the aquatic network and should\nnot be taken as a comprehensive survey of all possible road-related barriers."

        else:
            # drop species habitat columns that have no useful data
            spp_cols = [c for c in df.column_names if "Habitat" in c and c != "FishHabitatPartnership"]
            drop_cols = [c for c in spp_cols if pc.max(df[c]).as_py() <= 0]
            if len(drop_cols) > 0:
                df = df.drop(drop_cols)

            # calculate custom ranks
            # NOTE: can only calculate ranks for those that have networks and are not excluded from ranking
            if custom:
                to_rank = df.filter(pc.equal(df["Ranked"], True))
                tiers = calculate_tiers(to_rank)
                # cast to int8 to allow setting -1 null values
                tiers = tiers.cast(pa.schema([pa.field(c, "int8") for c in tiers.column_names])).add_column(
                    0, to_rank.schema.field("id"), to_rank["id"]
                )

                # join back to full data frame
                df = df.join(tiers, "id")

                if len(to_rank) < len(df):
                    # fill missing values
                    df = pa.Table.from_pydict(
                        {
                            **{col: df[col] for col in df.column_names if col not in CUSTOM_TIER_FIELDS},
                            **{col: df[col].fill_null(-1) for col in df.column_names if col in CUSTOM_TIER_FIELDS},
                        }
                    )

                # Sort by HasNetwork, tier
                df = df.sort_by([("HasNetwork", "descending"), (f"{sort}_tier", "ascending")])

            else:
                # sort only HasNetwork
                df = df.sort_by([("HasNetwork", "descending")])

        df = unpack_domains(df.drop(["id"]))

    filename = (
        f"road_stream_crossings.{format}" if barrier_type == "road_crossings" else f"aquatic_barrier_ranks.{format}"
    )

    url = f"{request.base_url.scheme}://{request.base_url.netloc}"

    ### Get metadata
    readme = get_readme(
        filename=filename,
        barrier_type=barrier_type,
        fields=df.column_names,
        url=url,
        unit_ids=extractor.unit_ids,
        warnings=warnings,
    )
    terms = get_terms(url=url)

    if format == "csv":
        return zip_csv_response(
            df,
            filename=filename,
            extra_str={"README.txt": readme, "TERMS_OF_USE.txt": terms},
            extra_path={"SARP_logo.png": LOGO_PATH},
        )

    raise NotImplementedError("Other formats not yet supported")

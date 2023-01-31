from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc

from api.constants import (
    Layers,
    Scenarios,
    Formats,
    CUSTOM_TIER_FIELDS,
    DAM_EXPORT_FIELDS,
    SB_EXPORT_FIELDS,
    ROAD_CROSSING_API_FIELDS,
)
from api.lib.domains import unpack_domains
from api.lib.tiers import calculate_tiers
from api.logger import log, log_request
from api.data import dams, small_barriers, road_crossings
from api.dependencies import DamsRecordExtractor, BarriersRecordExtractor
from api.metadata import get_readme, get_terms
from api.response import zip_csv_response


### Include logo in download package
LOGO_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "ui/src/images/sarp_logo_highres.png"
)


MAX_CROSSINGS = 1e6  # limit to 1M crossings in downloads


router = APIRouter()


@router.get("/dams/{format}/{layer}")
def download_dams(
    request: Request,
    id: str,
    layer: Layers = "State",
    extractor: DamsRecordExtractor = Depends(),
    custom: bool = False,
    include_unranked=False,
    sort: Scenarios = "NCWC",
    format: Formats = "csv",
):
    """Download subset of dams or small barriers data.

    If `include_unranked` is `True`, all barriers in the summary units are downloaded.

    Path parameters:
    <layer> : one of LAYERS
    <format> : "csv"

    Query parameters:
    * id: list of ids
    * custom: bool (default: False); set to true to perform custom ranking of subset defined here
    * include_unranked: bool (default: False); set to true to include unranked barriers in output
    * sort: str, one of 'NC', 'WC', 'NCWC'
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    read_columns = ["id"] + [
        c for c in DAM_EXPORT_FIELDS if not c in CUSTOM_TIER_FIELDS
    ]

    df = extractor.extract(dams, columns=read_columns, ranked=not include_unranked)
    log.info(f"selected {len(df):,} dams for download")

    # calculate custom ranks
    # NOTE: can only calculate ranks for those that have networks and are not excluded from ranking
    if custom:
        to_rank = df.filter(pc.equal(df["Ranked"], True))
        tiers = calculate_tiers(to_rank)
        # cast to int8 to allow setting -1 null values
        tiers = tiers.cast(
            pa.schema([pa.field(c, "int8") for c in tiers.column_names])
        ).add_column(0, to_rank.schema.field("id"), to_rank["id"])

        # join back to full data frame
        df = df.join(tiers, "id")

        if len(to_rank) < len(df):
            # fill missing values
            df = pa.Table.from_pydict(
                {
                    **{
                        col: df[col]
                        for col in df.column_names
                        if not col in CUSTOM_TIER_FIELDS
                    },
                    **{
                        col: df[col].fill_null(-1)
                        for col in df.column_names
                        if col in CUSTOM_TIER_FIELDS
                    },
                }
            )

        # Sort by HasNetwork, tier
        df = df.sort_by([("HasNetwork", "descending"), (f"{sort}_tier", "ascending")])

    else:
        # sort only HasNetwork
        df = df.sort_by([("HasNetwork", "descending")])

    df = unpack_domains(df.drop(["id"]))

    filename = f"aquatic_barrier_ranks.{format}"

    ### Get metadata
    readme = get_readme(
        filename=filename,
        barrier_type="dams",
        fields=df.column_names,
        url=request.base_url,
        layer=extractor.layer,
        ids=extractor.ids.tolist(),
    )
    terms = get_terms(url=request.base_url)

    if format == "csv":
        return zip_csv_response(
            df,
            filename=filename,
            extra_str={"README.txt": readme, "TERMS_OF_USE.txt": terms},
            extra_path={"SARP_logo.png": LOGO_PATH},
        )

    raise NotImplementedError("Other formats not yet supported")


@router.get("/small_barriers/{format}/{layer}")
def download_barriers(
    request: Request,
    id: str,
    layer: Layers = "State",
    extractor: BarriersRecordExtractor = Depends(),
    custom: bool = False,
    include_unranked=False,
    sort: Scenarios = "NCWC",
    format: Formats = "csv",
):
    """Download subset of small barriers data.

    If `include_unranked` is `True`, all barriers in the summary units are downloaded.

    Path parameters:
    <layer> : one of LAYERS
    <format> : "csv"

    Query parameters:
    * id: list of ids
    * custom: bool (default: False); set to true to perform custom ranking of subset defined here
    * include_unranked: bool (default: False); set to true to include unranked barriers in output
    * sort: str, one of 'NC', 'WC', 'NCWC'
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    read_columns = ["id"] + [c for c in SB_EXPORT_FIELDS if not c in CUSTOM_TIER_FIELDS]

    df = extractor.extract(
        small_barriers, columns=read_columns, ranked=not include_unranked
    )
    log.info(f"selected {len(df):,} barriers for download")

    # calculate custom ranks
    # NOTE: can only calculate ranks for those that have networks and are not excluded from ranking
    if custom:
        to_rank = df.filter(pc.equal(df["Ranked"], True))
        tiers = calculate_tiers(to_rank)
        # cast to int8 to allow setting -1 null values
        tiers = tiers.cast(
            pa.schema([pa.field(c, "int8") for c in tiers.column_names])
        ).add_column(0, to_rank.schema.field("id"), to_rank["id"])

        # join back to full data frame
        df = df.join(tiers, "id")

        if len(to_rank) < len(df):
            # fill missing values
            df = pa.Table.from_pydict(
                {
                    **{
                        col: df[col]
                        for col in df.column_names
                        if not col in CUSTOM_TIER_FIELDS
                    },
                    **{
                        col: df[col].fill_null(-1)
                        for col in df.column_names
                        if col in CUSTOM_TIER_FIELDS
                    },
                }
            )

        # Sort by tier
        df.sort_by([("HasNetwork", "descending"), (f"{sort}_tier", "ascending")])

    else:
        # sort only HasNetwork
        df = df.sort_by([("HasNetwork", "descending")])

    df = unpack_domains(df.drop(["id"]))

    filename = f"aquatic_barrier_ranks.{format}"

    ### create readme and terms of use
    readme = get_readme(
        filename=filename,
        barrier_type="road-related barriers",
        fields=df.column_names,
        url=request.base_url,
        layer=extractor.layer,
        ids=extractor.ids.tolist(),
    )

    terms = get_terms(url=request.base_url)

    if format == "csv":
        return zip_csv_response(
            df,
            filename=filename,
            extra_str={"README.txt": readme, "TERMS_OF_USE.txt": terms},
            extra_path={"SARP_logo.png": LOGO_PATH},
        )

    raise NotImplementedError("Other formats not yet supported")


@router.get("/road_crossings/{format}/{layer}")
def download_crossings(
    request: Request,
    id: str,
    layer: Layers = "State",
    extractor: BarriersRecordExtractor = Depends(),
    format: Formats = "csv",
):
    """Download subset of road crossing data.

    Path parameters:
    <layer> : one of LAYERS
    <format> : "csv"

    Query parameters:
    * id: list of ids
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    # NOTE: id field is not used
    df = extractor.extract(road_crossings, columns=ROAD_CROSSING_API_FIELDS)
    log.info(f"selected {len(df):,} road crossings for download")

    if len(df) > MAX_CROSSINGS:
        log.warn("too many road crossings selected, rejected")
        raise HTTPException(status_code=400, detail="Too many items requested")

    df = unpack_domains(df)

    filename = f"potential_road_related_barriers.{format}"

    ### create readme and terms of use
    readme = get_readme(
        filename=filename,
        barrier_type="potential road-related barriers",
        fields=df.column_names,
        url=request.base_url,
        layer=extractor.layer,
        ids=extractor.ids.tolist(),
        warnings="this dataset includes potential road-related barriers derived from the USGS Road Crossings dataset (2022) that have not yet been assessed for impacts to aquatic organisms.  These only include those that were snapped to the aquatic network and should not be taken as a comprehensive survey of all possible road-related barriers.",
    )

    terms = get_terms(url=request.base_url)

    if format == "csv":
        return zip_csv_response(
            df,
            filename=filename,
            extra_str={"README.txt": readme, "TERMS_OF_USE.txt": terms},
            extra_path={"SARP_logo.png": LOGO_PATH},
        )

    raise NotImplementedError("Other formats not yet supported")

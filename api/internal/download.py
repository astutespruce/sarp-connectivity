from datetime import date
from hashlib import sha1
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.requests import Request
import pyarrow as pa

from api.constants import (
    Layers,
    Scenarios,
    Formats,
    unpack_domains,
    DAM_EXPORT_FIELDS,
    DAM_FILTER_FIELD_MAP,
    SB_EXPORT_FIELDS,
)
from api.logger import log, log_request
from analysis.rank.lib.tiers import calculate_tiers
from api.data import dams, barriers
from api.dependencies import DamsRecordExtractor, BarriersRecordExtractor
from api.metadata import get_readme, get_terms
from api.response import zip_csv_response, zip_file_response
from api.settings import CACHE_DIRECTORY


### Include logo in download package
LOGO_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "ui/src/images/sarp_logo_highres.png"
)

router = APIRouter()


@router.get("/dams/{format}/{layer}")
def download_dams(
    request: Request,
    id: str,
    layer: Layers = "State",
    extractor: DamsRecordExtractor = Depends(),
    custom: bool = False,
    unranked=False,
    sort: Scenarios = "NCWC",
    format: Formats = "csv",
):
    """Download subset of dams or small barriers data.

    If `unranked` is `True`, all barriers in the summary units are downloaded.

    Path parameters:
    <layer> : one of LAYERS
    <format> : "csv"

    Query parameters:
    * id: list of ids
    * custom: bool (default: False); set to true to perform custom ranking of subset defined here
    * unranked: bool (default: False); set to true to include unranked barriers in output
    * sort: str, one of 'NC', 'WC', 'NCWC'
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    filename = f"aquatic_barrier_ranks.{format}"

    # See if we already already cached the response;
    # we only do this for unfiltered states and the entire region (ranked or unranked)
    cache_filename = None
    has_filters = any(q for q in request.query_params if q in DAM_FILTER_FIELD_MAP)
    if layer == "State" and format == "csv" and id and not (has_filters or custom):
        state_hash = sha1(id.encode("UTF8")).hexdigest()
        suffix = "_ranked" if not unranked else ""
        cache_filename = CACHE_DIRECTORY / f"{state_hash}{suffix}_dams.zip"

    if cache_filename and cache_filename.exists():
        return zip_file_response(
            cache_filename, filename.replace(".csv", f"_{date.today().isoformat()}.zip")
        )

    df = extractor.extract(dams).to_pandas().set_index("id")

    # include unranked dams - these are joined back later
    if unranked:
        full_df = df.copy()

    # can only calculate ranks for those that have networks and are not excluded from ranking
    df = df.loc[df.Ranked]

    # calculate custom ranks
    if custom:
        df = df.join(calculate_tiers(df))

    if unranked:
        # join back to full dataset
        tier_cols = df.columns.difference(full_df.columns)
        df = full_df.join(df[tier_cols], how="left")

        df[tier_cols] = df[tier_cols].fillna(-1).astype("int8")

    log.info(f"selected {len(df):,} dams for download")

    # Sort by tier
    if f"{sort}_tier" in df.columns:
        df = df.sort_values(by=["HasNetwork", f"{sort}_tier"], ascending=[False, True])

    cols = [c for c in DAM_EXPORT_FIELDS if c in set(df.columns)]
    df = pa.Table.from_pandas(df[cols].reset_index(drop=True))
    df = unpack_domains(df)

    ### Get metadata
    readme = get_readme(
        filename=filename,
        barrier_type="dams",
        fields=df.schema.names,
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
            cache_filename=cache_filename,
        )

    raise NotImplementedError("Other formats not yet supported")


@router.get("/small_barriers/{format}/{layer}")
def download_barriers(
    request: Request,
    id: str,
    layer: Layers = "State",
    extractor: BarriersRecordExtractor = Depends(),
    custom: bool = False,
    unranked=False,
    sort: Scenarios = "NCWC",
    format: Formats = "csv",
):
    """Download subset of mall barriers data.

    If `unranked` is `True`, all barriers in the summary units are downloaded.

    Path parameters:
    <layer> : one of LAYERS
    <format> : "csv"

    Query parameters:
    * id: list of ids
    * custom: bool (default: False); set to true to perform custom ranking of subset defined here
    * unranked: bool (default: False); set to true to include unranked barriers in output
    * sort: str, one of 'NC', 'WC', 'NCWC'
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    filename = f"aquatic_barrier_ranks.{format}"

    # See if we already already cached the response;
    # we only do this for unfiltered states and the entire region (ranked or unranked)
    cache_filename = None
    has_filters = any(q for q in request.query_params if q in DAM_FILTER_FIELD_MAP)
    if layer == "State" and format == "csv" and id and not (has_filters or custom):
        state_hash = sha1(id.encode("UTF8")).hexdigest()
        suffix = "_ranked" if not unranked else ""
        cache_filename = CACHE_DIRECTORY / f"{state_hash}{suffix}_small_barriers.zip"

    if cache_filename and cache_filename.exists():
        return zip_file_response(
            cache_filename, filename.replace(".csv", f"_{date.today().isoformat()}.zip")
        )

    df = extractor.extract(barriers).to_pandas().set_index("id")

    # include unranked barriers - these are joined back later
    if unranked:
        full_df = df.copy()

    # can only calculate ranks for those that have networks
    df = df.loc[df.Ranked]

    # calculate custom ranks
    if custom:
        df = df.join(calculate_tiers(df))

    if unranked:
        # join back to full dataset
        tier_cols = df.columns.difference(full_df.columns)
        df = full_df.join(df[tier_cols], how="left")

        df[tier_cols] = df[tier_cols].fillna(-1).astype("int8")

    log.info(f"selected {len(df):,} barriers for download")

    # Sort by tier
    if f"{sort}_tier" in df.columns:
        df = df.sort_values(by=["HasNetwork", f"{sort}_tier"], ascending=[False, True])

    cols = [c for c in SB_EXPORT_FIELDS if c in set(df.columns)]
    df = pa.Table.from_pandas(df[cols].reset_index(drop=True))
    df = unpack_domains(df)

    ### create readme and terms of use
    readme = get_readme(
        filename=filename,
        barrier_type="road-related barriers",
        fields=df.schema.names,
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
            cache_filename=cache_filename,
        )

    raise NotImplementedError("Other formats not yet supported")

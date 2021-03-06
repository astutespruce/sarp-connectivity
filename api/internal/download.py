from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.requests import Request


from api.constants import (
    Scenarios,
    Formats,
    unpack_domains,
    DAM_EXPORT_FIELDS,
    SB_EXPORT_FIELDS,
)
from api.logger import log, log_request
from analysis.rank.lib.tiers import calculate_tiers
from api.data import dams, barriers
from api.dependencies import DamsRecordExtractor, BarriersRecordExtractor
from api.metadata import get_readme, get_terms
from api.response import zip_csv_response


### Include logo in download package
LOGO_PATH = (
    Path(__file__).resolve().parent.parent.parent / "ui/src/images/sarp_logo.png"
)

router = APIRouter()


@router.get("/dams/{format}/{layer}")
def download_dams(
    request: Request,
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

    df = extractor.extract(dams).copy()

    # include unranked dams - these are joined back later
    if unranked:
        full_df = df.copy()

    # can only calculate ranks for those that have networks
    df = df.loc[df.HasNetwork]

    # calculate custom ranks
    if custom:
        df = calculate_tiers(df)

    if unranked:
        # join back to full dataset
        tier_cols = df.columns.difference(full_df.columns)
        df = full_df.join(df[tier_cols], how="left")

        df[tier_cols] = df[tier_cols].fillna(-1).astype("int8")

    log.info(f"selected {len(df)} dams for download")

    df = df[df.columns.intersection(DAM_EXPORT_FIELDS)]

    # Sort by tier
    if f"{sort}_tier" in df.columns:
        sort_field = f"{sort}_tier"
    else:
        sort_field = f"SE_{sort}_tier"

    df = df.sort_values(by=["HasNetwork", sort_field], ascending=[False, True])

    df = unpack_domains(df)

    ### Get metadata
    filename = f"aquatic_barrier_ranks_{date.today().isoformat()}.{format}"

    readme = get_readme(
        filename=filename,
        barrier_type="dams",
        fields=df.columns,
        url=request.base_url,
        layer=extractor.layer,
        ids=extractor.ids,
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


@router.get("/barriers/{format}/{layer}")
def download_barriers(
    request: Request,
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

    df = extractor.extract(barriers).copy()

    # include unranked barriers - these are joined back later
    if unranked:
        full_df = df.copy()

    # can only calculate ranks for those that have networks
    df = df.loc[df.HasNetwork]

    # calculate custom ranks
    if custom:
        df = calculate_tiers(df)

    if unranked:
        # join back to full dataset
        tier_cols = df.columns.difference(full_df.columns)
        df = full_df.join(df[tier_cols], how="left")

        df[tier_cols] = df[tier_cols].fillna(-1).astype("int8")

    log.info(f"selected {len(df)} barriers for download")

    df = df[df.columns.intersection(SB_EXPORT_FIELDS)]

    # Sort by tier
    if f"{sort}_tier" in df.columns:
        sort_field = f"{sort}_tier"
    else:
        sort_field = f"SE_{sort}_tier"

    df = df.sort_values(by=["HasNetwork", sort_field], ascending=[False, True])

    df = unpack_domains(df)

    filename = "aquatic_barrier_ranks_{0}.{1}".format(date.today().isoformat(), format)

    ### create readme and terms of use
    readme = get_readme(
        filename=filename,
        barrier_type="road-related barriers",
        fields=df.columns,
        url=request.base_url,
        layer=extractor.layer,
        ids=extractor.ids,
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
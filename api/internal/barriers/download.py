from datetime import datetime
from io import BytesIO
import os
from pathlib import Path
from time import time
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

import arq
from arq.jobs import Job, JobStatus
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pyarrow.csv import write_csv

from api.constants import (
    FullySupportedBarrierTypes,
    Scenarios,
    Formats,
    CUSTOM_TIER_FIELDS,
    DAM_EXPORT_FIELDS,
    SB_EXPORT_FIELDS,
    COMBINED_EXPORT_FIELDS,
    ROAD_CROSSING_EXPORT_FIELDS,
    LOGO_PATH,
)
from api.logger import log, log_request
from api.dependencies import get_unit_ids, get_filter_params
from api.lib.download import extract_for_download
from api.lib.extract import get_record_count
from api.lib.progress import get_progress, set_progress
from api.metadata import get_readme, get_terms
from api.settings import MAX_IMMEDIATE_DOWNLOAD_RECORDS, CUSTOM_DOWNLOAD_DIR, REDIS, REDIS_QUEUE


router = APIRouter()


@router.post("/{barrier_type}/{format}")
async def download(
    request: Request,
    barrier_type: FullySupportedBarrierTypes,
    format: Formats = "csv",
    unit_ids: get_unit_ids = Depends(),
    filters: get_filter_params = Depends(),
    custom_rank: bool = False,
    include_unranked: bool = False,
    sort: Scenarios = "NCWC",
):
    """Download subset of barrier_type data.

    If `include_unranked` is `True`, all barriers in the summary units are downloaded.

    Query parameters:
    * one more more ids (comma delimited) for each of the unit types, e.g., State=OR,WA (see get_unit_ids())
    * custom_rank: bool (default: False); set to true to perform custom ranking of subset defined here
    * include_unranked: bool (default: False); set to true to include unranked barriers in output
    * sort: Scenarios
    * filters are defined using a lowercased version of column name and a comma-delimited list of values (see get_filters())
    """

    log_request(request)

    if len(unit_ids) == 0 and len(filters) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one summary unit layer must have ids present or at least one filter must be defined",
        )

    # ranking is not applicable to road crossings
    ranked_only = not (include_unranked or barrier_type == "road_crossings")
    count = get_record_count(barrier_type, unit_ids=unit_ids, filters=filters, ranked_only=ranked_only)

    if count > MAX_IMMEDIATE_DOWNLOAD_RECORDS:
        log.info(f"selected {count:,} {barrier_type.replace('_', ' ')} for download via background task")

        # create custom download task and do this in the background
        try:
            redis = await arq.create_pool(REDIS)
            job = await redis.enqueue_job(
                "custom_download_task",
                barrier_type=barrier_type,
                format=format,
                unit_ids=unit_ids,
                filters=filters,
                custom_rank=custom_rank,
                ranked_only=ranked_only,
                sort=sort,
                _queue_name=REDIS_QUEUE,
            )

            return JSONResponse(content={"job": job.job_id})

        except Exception as ex:
            log.error(f"Error creating background task, is Redis offline?  {ex}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

        finally:
            await redis.aclose()

    log.info(f"selected {count:,} {barrier_type.replace('_', ' ')} for immediate download")

    barrier_type = barrier_type.value
    format = format.value
    sort = sort.value

    columns = ["id"]
    warnings = None
    match barrier_type:
        case "dams":
            columns += DAM_EXPORT_FIELDS
        case "small_barriers":
            columns += SB_EXPORT_FIELDS
        case "combined_barriers" | "largefish_barriers" | "smallfish_barriers":
            columns += COMBINED_EXPORT_FIELDS
        case "road_crossings":
            columns += ROAD_CROSSING_EXPORT_FIELDS
            warnings = "this dataset includes road/stream crossings (potential barriers) derived\nfrom the USGS Road Crossings dataset (2022) or USFS National Road / Stream crossings dataset (2024)\nthat have not yet been assessed for impacts to aquatic organisms.  Unsurveyed\ncrossings are limited to those that were snapped to the aquatic network and should\nnot be taken as a comprehensive survey of all possible road-related barriers."

    columns = [c for c in columns if c not in CUSTOM_TIER_FIELDS]

    df = extract_for_download(
        barrier_type,
        unit_ids=unit_ids,
        filters=filters,
        columns=columns,
        ranked_only=ranked_only,
        custom_rank=custom_rank,
        sort=sort,
    )

    tmp_dir = Path(tempfile.mkdtemp(dir=CUSTOM_DOWNLOAD_DIR))
    # grant permissions to Caddy to read from this directory; the default is too restrictive
    os.chmod(tmp_dir, 0o755)

    filename = f"road_stream_crossings.{format}" if barrier_type == "road_crossings" else f"{barrier_type}.{format}"

    ### Get metadata
    readme = get_readme(
        filename=filename,
        barrier_type=barrier_type,
        fields=df.column_names,
        unit_ids=unit_ids,
        warnings=warnings,
    )
    terms = get_terms()

    # other types will be rejected above
    if format == "csv":
        with open(tmp_dir / f"{barrier_type}.zip", "wb") as out:
            with ZipFile(out, "w", compression=ZIP_DEFLATED, compresslevel=5) as zf:
                csv_stream = BytesIO()
                write_csv(df, csv_stream)
                zf.writestr(filename, csv_stream.getvalue())
                zf.writestr("README.txt", readme)
                zf.writestr("TERMS_OF_USE.txt", terms)
                zf.write(LOGO_PATH, "SARP_logo.png")

        return JSONResponse(
            content={"status": "success", "path": f"/downloads/custom/{tmp_dir.name}/{barrier_type}.zip"}
        )


async def custom_download_task(
    ctx,
    barrier_type: FullySupportedBarrierTypes,
    unit_ids: dict,
    filters: dict,
    format: Formats,
    custom_rank: bool,
    ranked_only: bool,
    sort: Scenarios,
):
    await set_progress(ctx["redis"], ctx["job_id"], "0", "Extracting data")

    barrier_type = barrier_type.value
    format = format.value
    sort = sort.value

    columns = ["id"]
    warnings = None
    match barrier_type:
        case "dams":
            columns += DAM_EXPORT_FIELDS
        case "small_barriers":
            columns += SB_EXPORT_FIELDS
        case "combined_barriers" | "largefish_barriers" | "smallfish_barriers":
            columns += COMBINED_EXPORT_FIELDS
        case "road_crossings":
            columns += ROAD_CROSSING_EXPORT_FIELDS
            warnings = "this dataset includes road/stream crossings (potential barriers) derived\nfrom the USGS Road Crossings dataset (2022) or USFS National Road / Stream crossings dataset (2024)\nthat have not yet been assessed for impacts to aquatic organisms.  Unsurveyed\ncrossings are limited to those that were snapped to the aquatic network and should\nnot be taken as a comprehensive survey of all possible road-related barriers."

    columns = [c for c in columns if c not in CUSTOM_TIER_FIELDS]

    df = extract_for_download(
        barrier_type,
        unit_ids=unit_ids,
        filters=filters,
        columns=columns,
        custom_rank=custom_rank,
        ranked_only=ranked_only,
        sort=sort,
    )

    await set_progress(ctx["redis"], ctx["job_id"], "50", "Creating zip file")

    tmp_dir = Path(tempfile.mkdtemp(dir=CUSTOM_DOWNLOAD_DIR))
    # grant permissions to Caddy to read from this directory; the default is too restrictive
    os.chmod(tmp_dir, 0o755)

    filename = f"road_stream_crossings.{format}" if barrier_type == "road_crossings" else f"{barrier_type}.{format}"

    ### Get metadata
    readme = get_readme(
        filename=filename,
        barrier_type=barrier_type,
        fields=df.column_names,
        unit_ids=unit_ids,
        warnings=warnings,
    )
    terms = get_terms()

    # other types will be rejected before calling into this
    if format == "csv":
        with open(tmp_dir / f"{barrier_type}.zip", "wb") as out:
            with ZipFile(out, "w", compression=ZIP_DEFLATED, compresslevel=5) as zf:
                csv_stream = BytesIO()
                write_csv(df, csv_stream)
                zf.writestr(filename, csv_stream.getvalue())
                zf.writestr("README.txt", readme)
                zf.writestr("TERMS_OF_USE.txt", terms)
                zf.write(LOGO_PATH, "SARP_logo.png")

    await set_progress(ctx["redis"], ctx["job_id"], "100", "All done")

    return f"{tmp_dir.name}/{barrier_type}.zip"


@router.get("/downloads/status/{job_id}")
async def get_download_job_status(job_id: str):
    """Return the status of a download job.

    Job status values derived from JobStatus enum at:
    https://github.com/samuelcolvin/arq/blob/master/arq/jobs.py
    ['deferred', 'queued', 'in_progress', 'complete', 'not_found']

    We add ['success', 'failed'] status values here.

    Parameters
    ----------
    job_id : str

    Returns
    -------
    JSON
        {"status": "...", "progress": 0-100, "result": "...only if complete...", "detail": "...only if failed..."}
    """

    # loop until return or hit number of retries in case of redis timeout
    retry = 0
    while retry <= 5:
        redis = None

        try:
            redis = await arq.create_pool(REDIS)

            job = Job(job_id, redis=redis, _queue_name=REDIS_QUEUE)
            job_status = await job.status()

            if job_status == JobStatus.not_found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found; it may have been cancelled, timed out, or the server restarted.  Please try again.",
                )

            # TODO: proof by turning off redis
            if job_status == JobStatus.queued:
                job_info = await job.info()
                elapsed_time = datetime.now(tz=job_info.enqueue_time.tzinfo) - job_info.enqueue_time

                queued = [
                    j[0]
                    for j in sorted(
                        [(job.job_id, job.enqueue_time) for job in await redis.queued_jobs(queue_name=REDIS_QUEUE)],
                        key=lambda x: x[1],
                    )
                ]

                return JSONResponse(
                    content={
                        "status": job_status,
                        "progress": 0,
                        "queue_position": queued.index(job_id),
                        "elapsed_time": elapsed_time.seconds,
                    }
                )

            if job_status != JobStatus.complete:
                progress, message = await get_progress(redis, job_id)

                return JSONResponse(
                    content={
                        "status": job_status,
                        "progress": progress,
                        "message": message,
                    }
                )

            info = await job.result_info()

            try:
                # this re-raises the underlying exception raised in the worker
                zip_filename = await job.result()

                if info.success:
                    return JSONResponse(
                        content={
                            "status": "success",
                            "path": f"/downloads/custom/{zip_filename}",
                        }
                    )

            # raise timeout to outer retry loop
            except TimeoutError as ex:
                raise ex

            except Exception as ex:
                log.error(ex)
                message = "Internal server error"
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error",
                )

            return JSONResponse(content={"status": "failed", "detail": message})

        # in case we hit a Redis timeout while polling job status, make sure we don't break until connection cannot be re-established
        except TimeoutError as ex:
            retry += 1
            log.error(f"Redis connection timeout, retry {retry}")
            time.sleep(1)

            if retry >= 5:
                raise ex

        finally:
            if redis is not None:
                await redis.aclose()

from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

from fastapi.responses import Response, FileResponse
from pyarrow.feather import write_feather
from pyarrow.csv import write_csv


def csv_response(df, bounds=None):
    """Write data frame to CSV and return Response with proper headers

    Parameters
    ----------
    df : pyarrow Table
    bounds : list-like of [xmin, ymin, xmax, ymax], optional (default: None)

    Returns
    -------
    fastapi Response
    """

    csv_stream = BytesIO()
    cols = [c.lower() for c in df.schema.names]
    write_csv(df.rename_columns(cols).combine_chunks(), csv_stream)

    response = Response(content=csv_stream.getvalue(), media_type="text/csv")

    if bounds is not None:
        response.headers["X-BOUNDS"] = ",".join(str(b) for b in bounds)

    return response


def feather_response(df, bounds=None):
    """Write data frame to feather (Arrow IPC) and return Response with proper headers

    Parameters
    ----------
    df : pyarrow Table
    bounds : list-like of [xmin, ymin, xmax, ymax], optional (default: None)

    Returns
    -------
    fastapi Response
    """

    cols = [c.lower() for c in df.schema.names]
    table = df.rename_columns(cols)

    # discard pandas metadata and set bounds
    table = table.replace_schema_metadata(
        {"bounds": ",".join(str(b) for b in bounds) if bounds is not None else ""}
    )

    stream = BytesIO()
    write_feather(
        table,
        stream,
        compression="uncompressed",
    )
    response = Response(
        content=stream.getvalue(), media_type="application/octet-stream"
    )

    return response


def zip_csv_response(
    df, filename, extra_str=None, extra_path=None, cache_filename=None
):
    """Write data frame into CSV and include optional files within zip file.

    Parameters
    ----------
    df : parrow.Table
    filename : str
        output filename in zip file
    extra_str : dict, optional
        if present, provides a mapping between target filenames and string content
    extra_path : dict, optional
        if present, provides a mapping between target filenames and source filenames,
        for binary file inputs
    cache_filename : str, optional
        if present, the filename to be used for caching this response for future use

    Returns
    -------
    fastapi Response
    """

    zip_stream = BytesIO()
    with ZipFile(zip_stream, "w", compression=ZIP_DEFLATED, compresslevel=5) as zf:
        csv_stream = BytesIO()
        # combine_chunks() is necessary to avoid repeated headers
        write_csv(df.combine_chunks(), csv_stream)
        zf.writestr(filename, csv_stream.getvalue())

        if extra_str is not None:
            for path, value in extra_str.items():
                zf.writestr(path, value)

        if extra_path is not None:
            for target_path, src_path in extra_path.items():
                zf.write(src_path, target_path)

    if cache_filename:
        with open(cache_filename, "wb") as out:
            out.write(zip_stream.getvalue())
            zip_stream.seek(0)

    return Response(
        content=zip_stream.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename.replace('.csv', '.zip')}"
        },
    )


def zip_file_response(src_filename, out_filename):
    return FileResponse(
        src_filename,
        media_type="application/zip",
        filename=out_filename,
    )

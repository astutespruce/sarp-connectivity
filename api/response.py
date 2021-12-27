from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

from fastapi.responses import Response, FileResponse


def csv_response(df, bounds=None):
    """Write data frame to CSV and return Response with proper headers

    Parameters
    ----------
    df : DataFrame
    bounds : list-like of [xmin, ymin, xmax, ymax], optional (default: None)

    Returns
    -------
    fastapi Response
    """

    csv = df.to_csv(index_label="id", header=[c.lower() for c in df.columns])
    response = Response(content=csv, media_type="text/csv")

    if bounds is not None:
        response.headers["X-BOUNDS"] = ",".join(str(b) for b in bounds)

    return response


def zip_csv_response(
    df, filename, extra_str=None, extra_path=None, cache_filename=None
):
    """Write data frame into CSV and include optional files within zip file.

    Parameters
    ----------
    df : DataFrame
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
        zf.writestr(filename, df.to_csv(index=False))

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
        src_filename, media_type="application/zip", filename=out_filename,
    )

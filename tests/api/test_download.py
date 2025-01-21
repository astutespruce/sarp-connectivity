from io import BytesIO
from pathlib import Path
import time
from zipfile import ZipFile

import numpy as np
from pyarrow.csv import read_csv
import pytest

from api.constants import STATES
from api.settings import CUSTOM_DOWNLOAD_DIR


DELAY = 0.5  # seconds
POLL_ATTEMPTS = 30
TMP_DIR = Path("/tmp/sarp-download-test")
TMP_DIR.mkdir(exist_ok=True)


def get_csv_filename(barrier_type):
    return "road_stream_crossings.csv" if barrier_type == "road_crossings" else f"{barrier_type}.csv"


def verify_zip_contents(barrier_type, zip_filename):
    with ZipFile(zip_filename) as zf:
        names = set(zf.namelist())
        assert get_csv_filename(barrier_type) in names
        assert "README.txt" in names
        assert "TERMS_OF_USE.txt" in names
        assert "SARP_logo.png" in names


async def download_zip(client, path, outfilename):
    response = await client.get(path)
    assert response.status_code == 200

    filename = Path(path).name
    zip_filename = TMP_DIR / filename
    print(f"downloading to: {zip_filename}")
    with open(outfilename, "wb") as out:
        _ = out.write(response.read())


def extract_csv(barrier_type, zip_filename):
    buffer = BytesIO()
    with ZipFile(zip_filename) as zf:
        buffer.write(zf.read(get_csv_filename(barrier_type)))

    buffer.seek(0)
    return read_csv(buffer).to_pandas()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "barrier_type",
    ["dams", "small_barriers", "combined_barriers", "smallfish_barriers", "largefish_barriers", "road_crossings"],
)
@pytest.mark.parametrize("state", ["VI"])
async def test_small_download(client, barrier_type, state):
    try:
        # TODO: other params
        response = await client.post(f"/api/v1/internal/{barrier_type}/csv", params={"State": state})
        assert response.status_code == 200

        path = response.json().get("path")
        assert path

        # fetch the file and inspect the contents
        filename = Path(path).name
        zip_filename = TMP_DIR / filename
        await download_zip(client, path, zip_filename)

        verify_zip_contents(barrier_type, zip_filename)

        df = extract_csv(barrier_type, zip_filename)
        assert np.array_equal(df.State.unique(), [STATES[state]])

    finally:
        # cleanup any files created above
        for p in CUSTOM_DOWNLOAD_DIR.glob("*.zip"):
            p.unlink()

        for p in TMP_DIR.glob("*.zip"):
            p.unlink()


# NOTE: this requires arq to be running
@pytest.mark.anyio
# NOTE: this needs to use a state that is over the threshold (MAX_IMMEDIATE_DOWNLOAD_RECORDS)
# for each type
@pytest.mark.parametrize(
    "barrier_type,state",
    [
        ("dams", "AR"),
        ("small_barriers", "OR"),
        ("combined_barriers", "AR"),
        ("smallfish_barriers", "AR"),
        ("largefish_barriers", "AR"),
        ("road_crossings", "PR"),
    ],
)
async def test_large_download(client, barrier_type, state):
    # TODO: other params
    try:
        response = await client.post(f"/api/v1/internal/{barrier_type}/csv", params={"State": state})
        assert response.status_code == 200

        data = response.json()
        job_id = data["job"]

        # poll until job is done
        for i in range(0, POLL_ATTEMPTS):
            r = await client.get(f"/api/v1/internal/downloads/status/{job_id}")
            assert r.status_code == 200

            json = r.json()
            status = json.get("status")
            progress = json.get("progress")
            message = json.get("message")

            if status == "success":
                path = json.get("path")
                assert path

                print(f"Path: {path}")

                # fetch the file and inspect the contents
                filename = Path(path).name
                zip_filename = TMP_DIR / filename
                await download_zip(client, path, zip_filename)

                verify_zip_contents(barrier_type, zip_filename)

                df = extract_csv(barrier_type, zip_filename)
                assert np.array_equal(df.State.unique(), [STATES[state]])

                break

            if status == "failed":
                pytest.fail(f"task failed: {json['detail']}")

            status_info = f' ({json.get("queue_position")} ahead in queue)' if status == "queued" else ""
            print(f"status: {status}{status_info}, progress: {progress}, message: {message}")

            time.sleep(DELAY)

        # fail if we hit max number of polling attempts
        assert i < POLL_ATTEMPTS

    finally:
        # cleanup any files created above
        for p in CUSTOM_DOWNLOAD_DIR.glob("*.zip"):
            p.unlink()

        for p in TMP_DIR.glob("*.zip"):
            p.unlink()

import os
import tempfile
import time
import pandas as pd

from flask import Flask, render_template, request, send_file

from data import rank_and_score

app = Flask(__name__)
app.config["DEBUG"] = True

DATA = pd.read_csv("sarp_dams.csv")


@app.route("/")
def main():
    return render_template("index.html", huc12s="")


@app.route("/", methods=["POST"])
def get_csv():
    string_input = request.form["hucs"]
    list_input = [x.strip() for x in string_input.split(",")]
    doc_name = "HUC12_report.csv"

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, doc_name)

        start = time.time()
        df = rank_and_score(list_input, DATA)
        end = time.time()
        print(str(end - start) + " seconds")

        csv = df.to_csv(path, sep=",")

        return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run()

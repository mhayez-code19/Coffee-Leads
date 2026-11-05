#!/usr/bin/env python3
"""Write site/leads.json from coffee_leads.db for the web page."""
import datetime as dt
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "coffee_leads.db")
OUT = os.path.join(HERE, "_site", "leads.json")

COLS = ["lead_key", "name", "alt_names", "address", "city", "state", "zip", "phone",
        "first_event_date", "last_event_date", "signals", "sources", "event_types",
        "record_count", "match_level", "chain", "score", "lat", "lon", "first_seen"]


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(f"SELECT {','.join(COLS)} FROM leads ORDER BY score DESC, first_event_date DESC").fetchall()
    last = con.execute("SELECT max(run_at) FROM runs").fetchone()[0]
    runs = [dict(zip(["source_id", "fetched", "matched", "error"], r)) for r in
            con.execute("SELECT source_id, fetched, matched, error FROM runs WHERE run_at=?", (last,))]
    with open(os.path.join(HERE, "sources.json")) as fh:
        srcs = {s["id"]: {"jurisdiction": s["jurisdiction"], "url": s.get("portal_url", "")}
                for s in json.load(fh)["sources"]}
    for r in runs:
        r.update(srcs.get(r["source_id"], {}))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump({"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                   "last_run": last, "runs": runs, "sources": srcs,
                   "cols": COLS, "rows": [["" if v is None else v for v in r] for r in rows]},
                  fh, separators=(",", ":"))
    print(f"wrote {len(rows)} leads -> {OUT}")


if __name__ == "__main__":
    main()

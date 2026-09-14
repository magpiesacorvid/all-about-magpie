#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import html
import json
import random
import re
import shutil
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile


BASE = "https://trillian.mit.edu/~jc/music/abc/Russia/"
STAMP = "20160421085256"
ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
OUT = ROOT / "output"

TARGETS = """ManchurianHills.abc
Metelitsa.abc
MotBarrikaderna.abc
OchiChorniya.abc
OtceNash.abc
Ozhidanie.abc
Ozhidanie.fmt
Ozhidanie1.abc
Ozhidanie2.abc
Ozhidanie_Dm.abc
Ozhidanie_Em.abc
PodMoskovniyeVechera.abc
Proshchay.abc
PustVsegda.abc
Sher1_B.abc
Sher1_C.abc
SlenderMountainAsh.abc
ToskaPoRodina.abc
ToskaWaltz.abc
Troika.abc
UralskayaRyabinushka.abc
YamshchikNeGoniLoshadey.abc
Alexandrovsky.abc
Alexandrovsky_B.abc
Alexandrovsky_C.abc
BielolitzaKruglolitza.abc
Bublichki.abc
Bulgar1.abc
DorogoyDalnoyu.abc
DveGitari.abc
Freilach5.abc
Hopak.abc
Hrizantemy.abc
InTheCityGarden.abc
Kalinka.abc
Karapyet_B.abc
Karapyet_B.hdr
Karapyet_C.abc
Karapyet_C.hdr
Kasatske.abc
Kasatske_B.abc
Kasatske_B.hdr
Kasatske_C.abc
Kasatske_C.hdr
Katinka.abc
Katyusha.abc
Katyusha_Dm.abc
Katyusha_Em.abc
Kohanochka.abc
Korobushka.abc
Korobushka_B.abc
Korobushka_C.abc
Lezginka.abc
LonelyAccordion.abc
MaailmanValot.abc""".splitlines()

assert len(TARGETS) == 55 and len(set(TARGETS)) == 55


def fetch(url: str, tries: int = 6):
    errors = []
    for attempt in range(tries):
        try:
            req = Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 Russia-ABC-Recovery/1.0",
                    "Accept": "text/plain,text/vnd.abc,*/*",
                },
            )
            with urlopen(req, timeout=15) as response:
                body = response.read()
                if not body:
                    raise ValueError("empty response")
                return body, response.geturl()
        except Exception as exc:
            errors.append(str(exc))
            if isinstance(exc, HTTPError) and exc.code in {429, 502, 503, 504}:
                retry_after = exc.headers.get("Retry-After")
                try:
                    wait = float(retry_after) if retry_after else 8 + attempt * 6
                except ValueError:
                    wait = 8 + attempt * 6
                time.sleep(min(45, wait) + random.random())
            else:
                time.sleep(min(12, 1.6**attempt) + random.random())
    raise RuntimeError(" | ".join(errors)[-2500:])


def decode_text(body: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1251", "cp1252", "latin-1"):
        try:
            return body.decode(encoding).replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError:
            pass
    return body.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n")


def is_error_page(text: str) -> bool:
    head = text[:2000]
    return bool(re.search(r"<(?:!doctype|html|head|body)\b", head, re.I))


def is_genuine(text: str, suffix: str) -> bool:
    if not text.strip() or is_error_page(text):
        return False
    if suffix in {".fmt", ".hdr"}:
        return True
    # Accept complete tunes and genuine ABC fragments whose headers live in a
    # companion .hdr. Reject index/error pages and arbitrary tiny responses.
    has_field = bool(re.search(r"(?m)^\s*(?:X|T|M|L|K|Q|R|C)\s*:", text))
    has_music = bool(
        re.search(r"(?m)^[^%\n]*[A-Ga-gz][^\n]*\|[^\n]*$", text)
        or re.search(r"(?m)^\s*[\^_=]?[A-Ga-gz][,']*[0-9/]*(?:\s|$)", text)
    )
    return has_field or (has_music and len(text.strip()) >= 20)


def archive_urls(original_http: str):
    urls = [f"https://web.archive.org/web/{STAMP}id_/{original_http}"]
    cdx = "https://web.archive.org/cdx/search/cdx?" + urlencode(
        {
            "url": original_http,
            "output": "json",
            "filter": "statuscode:200",
            "fl": "timestamp,original,digest",
            "collapse": "digest",
            "limit": "20",
        }
    )
    try:
        raw, _ = fetch(cdx, 2)
        rows = json.loads(raw.decode("utf-8"))
        for row in reversed(rows[1:]):
            urls.append(f"https://web.archive.org/web/{row[0]}id_/{row[1]}")
    except Exception:
        pass
    return list(dict.fromkeys(urls))


def recover(name: str):
    suffix = Path(name).suffix.lower()
    live = urljoin(BASE, name)
    errors = []
    original = urljoin(BASE.replace("https://", "http://"), name)
    exact_wayback = f"https://web.archive.org/web/{STAMP}id_/{original}"
    primary_attempts = [
        ("wayback-exact", exact_wayback),
        ("live", live),
        ("live-http", live.replace("https://", "http://", 1)),
    ]
    for kind, url in primary_attempts:
        try:
            if kind == "wayback-exact":
                time.sleep(6.5)
            body, final_url = fetch(url, 8 if kind == "wayback-exact" else (2 if kind == "live" else 1))
            text = decode_text(body)
            if is_genuine(text, suffix):
                return {
                    "target": name,
                    "status": "recovered",
                    "kind": kind,
                    "url": final_url,
                    "text": text.rstrip() + "\n",
                    "bytes": len(body),
                    "error": "",
                }
            errors.append(f"{kind}: response was not a genuine source body")
        except Exception as exc:
            errors.append(f"{kind}: {exc}")
    for url in archive_urls(original):
        if url == exact_wayback:
            continue
        kind = "wayback"
        try:
            body, final_url = fetch(url, 1)
            text = decode_text(body)
            if is_genuine(text, suffix):
                return {
                    "target": name,
                    "status": "recovered",
                    "kind": kind,
                    "url": final_url,
                    "text": text.rstrip() + "\n",
                    "bytes": len(body),
                    "error": "",
                }
            errors.append(f"{kind}: response was not a genuine source body")
        except Exception as exc:
            errors.append(f"{kind}: {exc}")
    return {
        "target": name,
        "status": "unresolved",
        "kind": "",
        "url": live,
        "text": "",
        "bytes": 0,
        "error": " || ".join(errors)[-4000:],
    }


def repair_text(value: str) -> str:
    value = html.unescape(value).strip()
    for encoding in ("latin-1", "cp1252"):
        if not any(mark in value for mark in ("Ã", "Â", "Ì", "â€")):
            break
        try:
            candidate = value.encode(encoding).decode("utf-8")
            if sum(value.count(x) for x in ("Ã", "Â", "Ì", "â€")) > sum(
                candidate.count(x) for x in ("Ã", "Â", "Ì", "â€")
            ):
                value = candidate
        except Exception:
            pass
    return re.sub(r"\s+", " ", value).strip(" ._-")


def fields(record: str, tag: str):
    values = []
    for match in re.finditer(rf"(?mi)^\s*{re.escape(tag)}\s*:\s*(.*?)\s*$", record):
        value = repair_text(match.group(1))
        if value:
            values.append(value)
    return values


def split_records(text: str):
    starts = list(re.finditer(r"(?m)^\s*X\s*:\s*.*$", text))
    if starts:
        preamble = text[: starts[0].start()].strip()
        reusable = "\n".join(
            line for line in preamble.splitlines() if line.lstrip().startswith(("%", "I:"))
        ).strip()
        records = []
        for index, match in enumerate(starts):
            end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
            record = text[match.start() : end].strip()
            if reusable:
                record = reusable + "\n" + record
            if re.search(r"(?m)^\s*K\s*:", record):
                records.append(record + "\n")
        return records
    if re.search(r"(?m)^\s*K\s*:", text):
        return ["X:1\n" + text.strip() + "\n"]
    return []


def fingerprint(record: str) -> str:
    kept = []
    ignored = set("XTCOZFNSHWw")
    for raw in record.splitlines():
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        match = re.match(r"^([A-Za-z+]):", line)
        if match and match.group(1) in ignored:
            continue
        kept.append(re.sub(r"\s+", "", line))
    return hashlib.sha256("\n".join(kept).encode("utf-8")).hexdigest()


def title_of(record: str, source: str, number: int) -> str:
    titles = fields(record, "T")
    generic = {
        "",
        "untitled",
        "unknown",
        "song",
        "tune",
        "waltz",
        "vals",
        "valssi",
        "polka",
        "polska",
        "march",
        "mazurka",
    }
    for title in titles:
        if title.casefold() not in generic and not re.fullmatch(
            r"(?:song|tune|vals|rev)\s*\d*", title, re.I
        ):
            return title
    return titles[0] if titles else f"{Path(source).stem} tune {number}"


def first_field(record: str, tag: str) -> str:
    values = fields(record, tag)
    return values[0].split()[0] if values else ""


def safe_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", repair_text(value))
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.replace("&", " and ")
    value = re.sub(r"['’]", "", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return re.sub(r"_+", "_", value)[:110] or "Untitled"


def write_csv(path: Path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    shutil.rmtree(WORK, ignore_errors=True)
    shutil.rmtree(OUT, ignore_errors=True)
    source_dir = WORK / "source_files"
    support_dir = WORK / "support_files"
    individual_dir = WORK / "individual"
    report_dir = WORK / "reports"
    for path in (source_dir, support_dir, individual_dir, report_dir, OUT):
        path.mkdir(parents=True, exist_ok=True)

    results = []
    with ThreadPoolExecutor(max_workers=1) as pool:
        futures = {pool.submit(recover, name): name for name in TARGETS}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(result["status"], result["target"], result["kind"], flush=True)
    results.sort(key=lambda result: TARGETS.index(result["target"]))

    recovered_by_name = {}
    for result in results:
        if result["status"] != "recovered":
            continue
        recovered_by_name[result["target"]] = result["text"]
        destination = support_dir if Path(result["target"]).suffix.lower() in {".hdr", ".fmt"} else source_dir
        (destination / result["target"]).write_text(
            result["text"], encoding="utf-8", newline="\n"
        )

    records = []
    parse_rows = []
    for result in results:
        if result["status"] != "recovered" or not result["target"].lower().endswith(".abc"):
            continue
        name = result["target"]
        parse_text = result["text"]
        companion = str(Path(name).with_suffix(".hdr"))
        header_used = ""
        if companion in recovered_by_name:
            combined = recovered_by_name[companion].rstrip() + "\n" + parse_text.lstrip()
            if re.search(r"(?m)^\s*K\s*:", combined):
                parse_text = combined
                header_used = companion
        extracted = split_records(parse_text)
        parse_rows.append(
            {
                "source_file": name,
                "companion_header_used": header_used,
                "records_extracted": len(extracted),
                "status": "parsed" if extracted else "recovered source; no complete tune record",
            }
        )
        for number, record in enumerate(extracted, 1):
            records.append(
                {
                    "record": record,
                    "source": name,
                    "number": number,
                    "fingerprint": fingerprint(record),
                }
            )

    groups = {}
    for record in records:
        groups.setdefault(record["fingerprint"], []).append(record)

    unique = []
    duplicates = []
    for fingerprint_value, group in groups.items():
        group.sort(
            key=lambda item: (
                len(fields(item["record"], "T"))
                + len(fields(item["record"], "C"))
                + len(fields(item["record"], "R")),
                len(item["record"]),
            ),
            reverse=True,
        )
        kept = group[0]
        kept["sources"] = sorted({item["source"] for item in group})
        unique.append(kept)
        for removed in group[1:]:
            duplicates.append(
                {
                    "fingerprint": fingerprint_value,
                    "removed_source": removed["source"],
                    "removed_record": removed["number"],
                    "kept_source": kept["source"],
                    "kept_record": kept["number"],
                    "title": title_of(kept["record"], kept["source"], kept["number"]),
                    "key": first_field(kept["record"], "K"),
                }
            )

    unique.sort(
        key=lambda item: (
            title_of(item["record"], item["source"], item["number"]).casefold(),
            first_field(item["record"], "K"),
            item["fingerprint"],
        )
    )

    used_names = set()
    title_rows = []
    merged = []
    for catalog_number, item in enumerate(unique, 1):
        title = title_of(item["record"], item["source"], item["number"])
        key = first_field(item["record"], "K")
        rhythm = first_field(item["record"], "R")
        stem = safe_name(title)
        filename = stem + ".abc"
        if filename.casefold() in used_names and key:
            filename = f"{stem}_K-{safe_name(key)}.abc"
        variant = 2
        while filename.casefold() in used_names:
            filename = f"{stem}_variant-{variant}.abc"
            variant += 1
        used_names.add(filename.casefold())

        lines = item["record"].strip().splitlines()
        x_index = next(
            (index for index, line in enumerate(lines) if re.match(r"^\s*X\s*:", line)),
            None,
        )
        if x_index is None:
            lines.insert(0, f"X:{catalog_number}")
            x_index = 0
        else:
            lines[x_index] = f"X:{catalog_number}"
        lines.insert(x_index + 1, "% Recovered source file(s): " + "; ".join(item["sources"]))
        clean_record = "\n".join(lines).rstrip() + "\n"
        (individual_dir / filename).write_text(
            clean_record, encoding="utf-8", newline="\n"
        )
        merged.append(clean_record)
        title_rows.append(
            {
                "filename": filename,
                "title": title,
                "key": key,
                "rhythm": rhythm,
                "source_files": "; ".join(item["sources"]),
                "notation_sha256": item["fingerprint"],
            }
        )

    (WORK / "Russia_Clean_Collection.abc").write_text(
        "\n\n".join(record.rstrip() for record in merged) + ("\n" if merged else ""),
        encoding="utf-8",
        newline="\n",
    )

    source_rows = [
        {
            "target": result["target"],
            "status": result["status"],
            "source_kind": result["kind"],
            "source_url": result["url"],
            "bytes": result["bytes"],
            "error": result["error"],
        }
        for result in results
    ]
    write_csv(
        report_dir / "SOURCE_RECOVERY.csv",
        source_rows,
        ["target", "status", "source_kind", "source_url", "bytes", "error"],
    )
    write_csv(
        report_dir / "PARSE_AUDIT.csv",
        parse_rows,
        ["source_file", "companion_header_used", "records_extracted", "status"],
    )
    write_csv(
        report_dir / "TITLE_INDEX.csv",
        title_rows,
        ["filename", "title", "key", "rhythm", "source_files", "notation_sha256"],
    )
    write_csv(
        report_dir / "DUPLICATES_REMOVED.csv",
        duplicates,
        [
            "fingerprint",
            "removed_source",
            "removed_record",
            "kept_source",
            "kept_record",
            "title",
            "key",
        ],
    )

    unresolved = [
        f"{result['target']}: {result['error']}"
        for result in results
        if result["status"] != "recovered"
    ]
    (report_dir / "UNRESOLVED.txt").write_text(
        "\n".join(unresolved) + "\n" if unresolved else "None\n", encoding="utf-8"
    )

    recovered = sum(result["status"] == "recovered" for result in results)
    recovered_abc = sum(
        result["status"] == "recovered" and result["target"].lower().endswith(".abc")
        for result in results
    )
    support = sum(
        result["status"] == "recovered" and not result["target"].lower().endswith(".abc")
        for result in results
    )
    unparsed = sum(row["records_extracted"] == 0 for row in parse_rows)
    report = f"""RUSSIA ABC RECOVERY - CLEANED COLLECTION
Requested source files: {len(TARGETS)}
Genuine files recovered: {recovered}
Recovered ABC files: {recovered_abc}
Recovered support files (.fmt/.hdr): {support}
Unresolved source files: {len(unresolved)}
Recovered ABC files without a complete parsed tune: {unparsed}
Tune records extracted: {len(records)}
Exact musical duplicates removed: {len(duplicates)}
Unique tune records packaged: {len(unique)}

RULES
No placeholder or fabricated ABC bodies were created.
All recovered originals are preserved unchanged apart from UTF-8/newline normalization.
Companion .hdr files are prepended for parsing when a matching ABC body needs them.
Multi-tune files are split at X: boundaries.
Exact duplicate comparison ignores catalogue, title, provenance and lyric fields.
Keys, notation, chords, voices and parts remain in the comparison, so alternate
keys and genuinely different arrangements are preserved.
Every unique tune is named from its internal T: title; collisions receive a key
or variant suffix. All unique records are merged into Russia_Clean_Collection.abc.
"""
    (report_dir / "RECOVERY_REPORT.txt").write_text(report, encoding="utf-8")
    (WORK / "README.txt").write_text(
        """RUSSIA ABC CLEANED COLLECTION
Russia_Clean_Collection.abc - all unique tunes merged
individual/ - one real-title file per unique tune
source_files/ - recovered original ABC source bodies
support_files/ - recovered .fmt and .hdr companion files
reports/ - recovery, parsing, title, duplicate and unresolved audits
""",
        encoding="utf-8",
    )

    zip_path = OUT / "Russia_ABCs_complete_cleaned.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(WORK.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(WORK))
    with ZipFile(zip_path) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise RuntimeError("bad ZIP member: " + bad_member)
        names = archive.namelist()
        if "Russia_Clean_Collection.abc" not in names:
            raise RuntimeError("merged collection absent")
        if not any(name.startswith("individual/") for name in names):
            raise RuntimeError("individual collection absent")

    print(report, flush=True)
    if recovered < 45:
        raise RuntimeError(f"catastrophic recovery: only {recovered}/{len(TARGETS)} files")


if __name__ == "__main__":
    main()

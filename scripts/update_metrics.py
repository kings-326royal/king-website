#!/usr/bin/env python3
"""Fetch citation metrics for the profile site and write metrics.js.

Sources (each optional, each kept from the previous run if it fails):
  - Google Scholar profile page (no key needed)        -> profile "scholar" id in data.js
  - Scopus Search API (needs SCOPUS_API_KEY)            -> profile "scopus" author id
  - Web of Science Starter API (needs WOS_API_KEY)      -> profile "wos" researcher id

Run locally:  python3 scripts/update_metrics.py
GitHub Actions runs it weekly (.github/workflows/update-metrics.yml).
"""
import datetime, html, json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data.js")
OUT = os.path.join(ROOT, "metrics.js")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
TODAY = datetime.date.today().isoformat()


def load_js(path, var):
    if not os.path.exists(path):
        return None
    s = open(path, encoding="utf-8").read()
    m = re.search(r"window\." + var + r"\s*=\s*(\{.*\})\s*;?\s*$", s, re.S)
    return json.loads(m.group(1)) if m else None


def get(url, headers=None, tries=3):
    req = urllib.request.Request(url, headers=dict({"User-Agent": UA, "Accept-Language": "en"}, **(headers or {})))
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            if k == tries - 1:
                raise
            time.sleep(4 * (k + 1))


def h_index(cites):
    c = sorted((int(x or 0) for x in cites), reverse=True)
    return sum(1 for i, v in enumerate(c, 1) if v >= i)


def scholar(uid):
    base = "https://scholar.google.com/citations?hl=en&user=" + urllib.parse.quote(uid)
    page = get(base + "&pagesize=100")
    std = [int(x) for x in re.findall(r'class="gsc_rsb_std">(\d+)<', page)]
    if len(std) < 6:
        raise RuntimeError("profile page did not contain the citation table (blocked or changed)")
    by_year = []
    hb = page.find('<div class="gsc_md_hist_b">')
    if hb >= 0:
        seg = page[hb:page.find("</div>", hb)]
        years = [int(y) for y in re.findall(r'class="gsc_g_t[^"]*"[^>]*>(\d{4})<', seg)]
        counts = {}
        for z, c in re.findall(r'class="gsc_g_a"[^>]*z-index:(\d+)[^>]*><span class="gsc_g_al">(\d+)<', seg):
            idx = len(years) - int(z)  # Scholar stacks bars so the oldest year has the highest z-index
            if 0 <= idx < len(years):
                counts[years[idx]] = int(c)
        by_year = [{"year": y, "citations": counts.get(y, 0)} for y in years]
    pubs, start = [], 0
    while True:
        chunk = page if start == 0 else get(base + "&pagesize=100&cstart=%d" % start)
        rows = re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', chunk, re.S)
        for r in rows:
            t = re.search(r'class="gsc_a_at"[^>]*>(.*?)</a>', r, re.S)
            v = re.findall(r'<div class="gs_gray">(.*?)</div>', r, re.S)
            c = re.search(r'class="gsc_a_ac[^"]*"[^>]*>(\d*)<', r)
            y = re.search(r'class="gsc_a_h gsc_a_hc gs_ibl"[^>]*>(\d{4})<', r) or re.search(r'>(\d{4})</span></td>', r)
            pubs.append({
                "title": html.unescape(re.sub("<[^>]+>", "", t.group(1))).strip() if t else "",
                "venue": html.unescape(re.sub("<[^>]+>", "", v[1])).strip() if len(v) > 1 else "",
                "year": y.group(1) if y else "",
                "citations": int(c.group(1)) if c and c.group(1) else 0,
            })
        if len(rows) < 100 or start > 900:
            break
        start += 100
        time.sleep(3)
    hdr = re.findall(r'<th class="gsc_rsb_sth">([^<]*)<', page)
    since = next((h for h in hdr if h.lower().startswith("since")), "")
    return {
        "citations": std[0], "citationsSince": std[1], "sinceLabel": since,
        "hIndex": std[2], "hIndexSince": std[3], "i10": std[4], "i10Since": std[5],
        "documents": len(pubs), "byYear": by_year,
        "top": sorted(pubs, key=lambda p: -p["citations"])[:10],
        "url": base, "updated": TODAY,
    }


def scopus(author_id, key):
    cites, docs, start, total = [], [], 0, None
    while True:
        q = urllib.parse.urlencode({"query": "AU-ID(%s)" % author_id, "count": 25, "start": start,
                                    "field": "dc:title,citedby-count,prism:coverDate,prism:publicationName"})
        d = json.loads(get("https://api.elsevier.com/content/search/scopus?" + q, {"X-ELS-APIKey": key, "Accept": "application/json"}))
        res = d.get("search-results", {})
        total = int(res.get("opensearch:totalResults", 0))
        for e in res.get("entry", []):
            if "error" in e:
                continue
            n = int(e.get("citedby-count") or 0)
            cites.append(n)
            docs.append({"title": e.get("dc:title", ""), "venue": e.get("prism:publicationName", ""),
                         "year": (e.get("prism:coverDate") or "")[:4], "citations": n})
        start += 25
        if start >= total or start >= 1000:
            break
    return {"documents": total, "citations": sum(cites), "hIndex": h_index(cites),
            "top": sorted(docs, key=lambda p: -p["citations"])[:10],
            "url": "https://www.scopus.com/authid/detail.uri?authorId=" + author_id, "updated": TODAY}


def wos(researcher_id, key):
    cites, docs, page, total = [], [], 1, None
    while True:
        q = urllib.parse.urlencode({"q": "AI=(%s)" % researcher_id, "db": "WOS", "limit": 50, "page": page})
        d = json.loads(get("https://api.clarivate.com/apis/wos-starter/v1/documents?" + q, {"X-ApiKey": key, "Accept": "application/json"}))
        total = int(d.get("metadata", {}).get("total", 0))
        for h in d.get("hits", []):
            n = sum(int(c.get("count") or 0) for c in h.get("citations", []) if c.get("db") == "WOS")
            cites.append(n)
            src = h.get("source", {})
            docs.append({"title": h.get("title", ""), "venue": src.get("sourceTitle", ""),
                         "year": str(src.get("publishYear", "")), "citations": n})
        if page * 50 >= total or page >= 20:
            break
        page += 1
    return {"documents": total, "citations": sum(cites), "hIndex": h_index(cites),
            "top": sorted(docs, key=lambda p: -p["citations"])[:10],
            "url": "https://www.webofscience.com/wos/author/record/" + researcher_id, "updated": TODAY}


def main():
    data = load_js(DATA, "CV_DATA") or {}
    prof = data.get("profile") or {}
    prev = load_js(OUT, "CV_METRICS") or {}
    out = {"updated": TODAY, "errors": {}}
    jobs = [
        ("scholar", prof.get("scholar"), lambda i: scholar(i), None),
        ("scopus", prof.get("scopus"), lambda i: scopus(i, os.environ["SCOPUS_API_KEY"]), "SCOPUS_API_KEY"),
        ("wos", prof.get("wos"), lambda i: wos(i, os.environ["WOS_API_KEY"]), "WOS_API_KEY"),
    ]
    for name, ident, fn, env in jobs:
        if not ident:
            continue
        if env and not os.environ.get(env):
            if prev.get(name):
                out[name] = prev[name]
            out["errors"][name] = "No %s set; add it as a repository secret to enable this source." % env
            continue
        try:
            out[name] = fn(ident.strip())
            print("%s: %s citations, h-index %s" % (name, out[name].get("citations"), out[name].get("hIndex")))
        except Exception as e:  # noqa: BLE001
            out["errors"][name] = "Last fetch failed (%s); showing the previous figures." % str(e)[:160]
            if prev.get(name):
                out[name] = prev[name]
            print("%s: failed: %s" % (name, e), file=sys.stderr)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("/* Citation metrics, written automatically by scripts/update_metrics.py. Do not edit by hand. */\n")
        f.write("window.CV_METRICS = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()

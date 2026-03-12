#!/usr/bin/env python3
from pathlib import Path
import re
import sys
from collections import defaultdict

concept_re = re.compile(r'^(ascl:([0-9]+))\s+a\s+skos:Concept\s*;')

SUPPLEMENTARY_CODES = {
    "00000000", "00000002", "11110000", "11111100", "11111200", "11111300",
    "11111400", "11111500", "11111600", "11111700", "11111800", "11112100",
    "11112200", "11112300", "11112400", "11112500", "11112600", "11112700",
    "11112800", "11113100", "11113200", "11113300", "11113400", "11113500",
    "11113600", "11113700", "11119900", "11121100", "11131100", "11141100",
    "11151100", "11161100", "11170000", "11171100", "11171200", "11179900",
    "11180000", "11181100", "11181200", "11189900", "11211100", "11221100",
    "11230000", "11231100", "11811100", "11999900", "12110000", "12111100",
    "12111200", "12119900", "12121100", "13110000", "13111100", "13120000",
    "13121100", "13121200", "13130000", "13131100", "13139900", "13141100",
    "13150000", "13151100", "13151200", "13159900", "13160000", "13161100",
    "13161200", "13169900", "13999900", "14110000", "14111100", "14999900",
    "15110000", "15111100", "15111200", "15120000", "15121100", "15129900",
    "15999900", "16111100", "16121100", "16999900", "17110000", "17111100",
    "17119900", "17120000", "17121100", "17121200", "17999900", "18111100",
    "18999900", "21111100", "21999900", "22111100", "23111100", "23120000",
    "23121100", "23121200", "23121300", "23129900", "24111100", "25111100",
    "26111100", "27110000", "27111100", "27111200", "27111300", "27111400",
    "27119900", "27999900", "91711100", "91981100", "91991100"
}

def parent_code(code: str) -> str | None:
    if code in SUPPLEMENTARY_CODES:
        return None
    n = len(code)
    if n == 2:
        return None
    if n == 4:
        return code[:2]
    if n == 6:
        return code[:4]
    if n == 8:
        return code[:6]
    return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 add_ascl_hierarchy.py input.ttl output.ttl")
        sys.exit(1)

    infile = Path(sys.argv[1])
    outfile = Path(sys.argv[2])

    text = infile.read_text(encoding="utf-8")
    lines = text.splitlines()

    concepts = []
    for line in lines:
        m = concept_re.match(line)
        if m:
            iri = m.group(1)
            code = m.group(2)
            concepts.append((iri, code))

    all_codes = {code for _, code in concepts}
    hierarchy_codes = {code for _, code in concepts if code not in SUPPLEMENTARY_CODES}

    broader_triples = []
    narrower_map = defaultdict(list)

    for iri, code in concepts:
        if code not in hierarchy_codes:
            continue
        parent = parent_code(code)
        if parent and parent in hierarchy_codes:
            parent_iri = f"ascl:{parent}"
            broader_triples.append(f"{iri} skos:broader {parent_iri} .")
            narrower_map[parent_iri].append(iri)

    narrower_triples = []
    for parent_iri, children in sorted(narrower_map.items()):
        for child_iri in sorted(children):
            narrower_triples.append(f"{parent_iri} skos:narrower {child_iri} .")

    out = text.rstrip() + "\n\n# Materialised hierarchy\n"
    out += "\n".join(broader_triples) + "\n\n"
    out += "\n".join(narrower_triples) + "\n"

    outfile.write_text(out, encoding="utf-8")

    print(f"Wrote {outfile}")
    print(f"Concepts found: {len(concepts)}")
    print(f"Supplementary codes ignored: {len([c for _, c in concepts if c in SUPPLEMENTARY_CODES])}")
    print(f"Added broader triples: {len(broader_triples)}")
    print(f"Added narrower triples: {len(narrower_triples)}")

if __name__ == "__main__":
    main()
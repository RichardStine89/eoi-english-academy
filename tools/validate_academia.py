"""Check public academy references, curriculum coverage and exam gates."""

from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
ACADEMY = ROOT / "docs" / "academia"
LEVELS = ("A1", "A2", "B1", "B2", "C1")
UNITS = {f"{level}-{number:02d}" for level in LEVELS for number in range(1, 13)}
LINK = re.compile(r"\[[^\]\n]+\]\(([^\s)]+)\)")


def validate_curriculum():
    curriculum = ROOT / "languages" / "english" / "curriculum"
    found = set()
    for level in LEVELS:
        for unit in (curriculum / level.lower()).glob("unit-*.md"):
            code = level + "-" + unit.stem.split("-", 1)[-1]
            found.add(code)
            assert unit.read_text(encoding="utf-8").lstrip().startswith("# "), unit
    assert found == UNITS, f"Unit files differ: {sorted(found ^ UNITS)}"

    matrix = (ACADEMY / "curriculo-eoi.md").read_text(encoding="utf-8")
    rows = Counter(re.findall(r"(?m)^\| \[((?:A[12]|B[12]|C1)-\d\d)\s+·", matrix))
    assert rows == Counter(UNITS), "The curriculum matrix must cover every unit exactly once"
    practice = (ACADEMY / "curriculo-practica.md").read_text(encoding="utf-8")
    resources = Counter(re.findall(r"(?m)^\| ((?:A[12]|B[12]|C1)-\d\d) \|", practice))
    assert resources == Counter(UNITS), "Each unit needs a resource row"
    pronunciation = (ACADEMY / "pronunciacion-por-unidad.md").read_text(encoding="utf-8")
    drills = Counter(re.findall(r"(?m)^\| ((?:A[12]|B[12]|C1)-\d\d) \|", pronunciation))
    assert drills == Counter(UNITS), "Each unit needs a pronunciation row"
    return len(found)


def slug(heading):
    heading = heading.strip().lower()
    return "".join(char for char in heading if char.isalnum() or char in " -_").replace(" ", "-")


def validate_links():
    checked = 0
    documents = [*ACADEMY.rglob("*.md"), ROOT / "modules" / "pronunciation-lab" / "README.md"]
    for document in documents:
        for link in LINK.findall(document.read_text(encoding="utf-8")):
            if re.match(r"(?i)^[a-z]+:", link):
                continue
            name, _, anchor = link.partition("#")
            target = (document.parent / unquote(name)).resolve() if name else document
            assert target.is_relative_to(ROOT) and target.exists(), f"{document.relative_to(ROOT)}: {link}"
            if anchor:
                content = target.read_text(encoding="utf-8")
                anchors = {slug(label) for label in re.findall(r"(?m)^#{1,6} (.+)$", content)}
                anchors.update(re.findall(r'<a\s+(?:id|name)="([^"]+)"', content))
                assert unquote(anchor) in anchors, f"{document.relative_to(ROOT)}: missing anchor {link}"
            checked += 1
    return checked


def validate_exam_gates():
    exams = ACADEMY / "examenes"
    assets = json.loads((exams / "catalogo.json").read_text(encoding="utf-8"))["archivos"]
    exam_rows = json.loads((exams / "convocatorias.json").read_text(encoding="utf-8"))["convocatorias"]
    exams_by_id = {entry["id"]: entry for entry in exam_rows}
    assert len(exams_by_id) == len(exam_rows) == 70
    assert len({asset["id"] for asset in assets}) == len(assets) == 442
    assert all(asset["convocatoria_id"] in exams_by_id for asset in assets)
    asset_ids = {asset["id"] for asset in assets}

    b1 = exams_by_id["B1-2024-06"]["solucionario"]["evaluacion_comto"]
    assert b1["estado"] == "apta" and b1["tareas_aptas"] == [1, 2, 3]
    assert sum(b1["maximo_por_tarea"]) == 26
    c1_june = exams_by_id["C1-2024-06"]["solucionario"]
    assert c1_june["evaluacion_comto"]["tareas_aptas"] == []
    a2 = exams_by_id["A2-MODELO-01"]["solucionario"]
    assert 1 in a2["evaluacion_comto"]["tareas_bloqueadas"]
    assert set(a2["exclusiones_correccion_automatica"]["preguntas"]) == {6, 8}

    eligible = 0
    for entry in exam_rows:
        reading = (entry.get("solucionario") or {}).get("evaluacion_comte")
        if not reading or not reading.get("cuadernillo"):
            continue
        assert reading["cuadernillo"] in asset_ids
        maxima = reading["maximo_por_tarea"]
        whole = set(reading["tareas_aptas"])
        closed = set(reading["tareas_bloqueadas"])
        partial = {int(task): set(items) for task, items in reading["preguntas_aptas"].items()}
        excluded = {int(task): set(items) for task, items in reading["preguntas_bloqueadas"].items()}
        assert not (whole & closed or whole & partial.keys() or closed & partial.keys())
        assert whole | closed | partial.keys() == set(range(1, len(maxima) + 1))
        assert excluded.keys() == partial.keys()
        for task, items in partial.items():
            assert not items & excluded[task]
            assert items | excluded[task] == set(range(1, maxima[task - 1] + 1))
        assert reading["puntuacion_total_autorizada"] == (len(whole) == len(maxima))
        eligible += sum(maxima[task - 1] for task in whole) + sum(map(len, partial.values()))
    return len(assets), len(exam_rows), eligible


def validate_external_references():
    index = ACADEMY / "examenes" / "recursos-externos-v1.2.json"
    resources = json.loads(index.read_text(encoding="utf-8"))["recursos"]
    assert len({row["id"] for row in resources}) == len(resources)
    for row in resources:
        original = urlsplit(row["url_original"])
        assert original.scheme == "https" and original.hostname, row["id"]
        assert not row["referencia_drive"] and original.hostname not in {"drive.google.com", "docs.google.com"}, row["id"]
        assert row["niveles"] and set(row["niveles"]) <= {*LEVELS, "C2"}, row["id"]
        assert row["estado"] and row["condiciones"] and row["restriccion"], row["id"]
    return len(resources)


def main():
    units = validate_curriculum()
    links = validate_links()
    assets, exams, items = validate_exam_gates()
    external = validate_external_references()
    print(f"{units} units, {links} internal links, {assets} inventory rows, {exams} exam sets, "
          f"{items} enabled COMTE items, {external} public external references")


if __name__ == "__main__":
    main()

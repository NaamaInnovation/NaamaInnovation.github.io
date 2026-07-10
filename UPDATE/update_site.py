import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path


UPDATE_DIR = Path(__file__).resolve().parent
ROOT = UPDATE_DIR.parent
PROJECTS_FILE = UPDATE_DIR / "Projects.xlsx"
EVENTS_FILE = UPDATE_DIR / "Event list.xlsx"
GALLERY_DIR = ROOT / "photos" / "Gallery"
WORKS_JSON = ROOT / "content" / "works.json"
EVENTS_JSON = ROOT / "content" / "events.json"
GALLERY_PAGE = ROOT / "gallery" / "index.html"

NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"pr": "http://schemas.openxmlformats.org/package/2006/relationships"}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".JPG", ".JPEG", ".PNG", ".GIF", ".WEBP"}


def fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def column_index(cell_ref):
    match = re.match(r"[A-Z]+", cell_ref or "A1")
    letters = match.group(0) if match else "A"
    index = 0
    for character in letters:
        index = index * 26 + ord(character) - 64
    return index - 1


def read_xlsx(path):
    if not path.exists():
        fail(f"Missing file: {path.relative_to(ROOT)}")

    with zipfile.ZipFile(path) as archive:
        shared_strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("a:si", NS):
                shared_strings.append("".join(text.text or "" for text in item.findall(".//a:t", NS)))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationship_map = {
            relationship.attrib["Id"]: relationship.attrib["Target"]
            for relationship in relationships.findall("pr:Relationship", REL_NS)
        }

        first_sheet = workbook.find("a:sheets/a:sheet", NS)
        if first_sheet is None:
            return []

        target = relationship_map[first_sheet.attrib[RID]]
        sheet_path = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
        sheet = ET.fromstring(archive.read(sheet_path))
        rows = []

        for row in sheet.findall(".//a:sheetData/a:row", NS):
            values = []
            for cell in row.findall("a:c", NS):
                index = column_index(cell.attrib.get("r"))
                while len(values) <= index:
                    values.append("")

                value_node = cell.find("a:v", NS)
                value = "" if value_node is None or value_node.text is None else value_node.text
                if cell.attrib.get("t") == "s" and value:
                    value = shared_strings[int(value)]
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(text.text or "" for text in cell.findall(".//a:t", NS))
                values[index] = value.strip() if isinstance(value, str) else value
            rows.append(values)

    return rows


def slug(value):
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return result or "item"


def get_cell(row, headers, *names):
    normalized = {header.lower().strip(): index for index, header in enumerate(headers)}
    for name in names:
        index = normalized.get(name.lower().strip())
        if index is not None and index < len(row):
            return str(row[index]).strip()
    return ""


def excel_date(value):
    if not re.fullmatch(r"\d+(\.0)?", value or ""):
        return value

    serial = int(float(value))
    if serial < 30000 or serial > 60000:
        return value

    date = datetime(1899, 12, 30) + timedelta(days=serial)
    return f"{date.day}.{date.month}.{date.year}"


def remove_empty_values(value):
    if isinstance(value, dict):
        return {key: remove_empty_values(item) for key, item in value.items() if item not in ("", None, {}, [])}
    return value


def build_projects():
    rows = read_xlsx(PROJECTS_FILE)
    if not rows:
        return []

    headers = [str(header).strip() for header in rows[0]]
    projects = []

    for index, row in enumerate(rows[1:], start=1):
        title = get_cell(row, headers, "Title")
        if not title:
            continue

        credits = {
            "Composition": get_cell(row, headers, "Composition"),
            "Performers": get_cell(row, headers, "Performers"),
            "Sound engineer": get_cell(row, headers, "Sound engineer"),
            "Electronics and sound design": get_cell(row, headers, "Electronics and sound design"),
            "Collaborators": get_cell(row, headers, "Colloborators", "Collaborators"),
            "Premiere": excel_date(get_cell(row, headers, "Premiere")),
        }

        videos = [
            get_cell(row, headers, "Youtube link 1", "YouTube link 1", "Youtube link", "YouTube link", "Video"),
            get_cell(row, headers, "Youtube link 2", "YouTube link 2"),
        ]
        videos = [video for video in videos if video]

        project = {
            "id": slug(title),
            "title": title,
            "subtitle": get_cell(row, headers, "sub-title", "Subtitle"),
            "description": get_cell(row, headers, "Third title", "Description"),
            "sortOrder": len(rows) - index,
            "videos": videos,
            "credits": credits,
            "published": True,
        }
        projects.append(remove_empty_values(project))

    return projects


def build_events(projects):
    rows = read_xlsx(EVENTS_FILE)
    if not rows:
        return []

    headers = [str(header).strip() for header in rows[0]]
    project_links = {project["title"].lower(): f"/works/#{project['id']}" for project in projects}
    events = []

    for row in rows[1:]:
        title = get_cell(row, headers, "Event name", "Title")
        date = excel_date(get_cell(row, headers, "Date"))
        location = get_cell(row, headers, "location", "Location")
        if not any([title, date, location]):
            continue

        details_url = get_cell(row, headers, "Details", "Details link", "Link")
        event = {
            "title": title,
            "date": date,
            "type": "upcoming",
            "location": location,
            "projectLink": project_links.get(title.lower(), ""),
            "detailsLink": details_url,
            "published": True,
        }
        events.append(remove_empty_values(event))

    return events


def gallery_images():
    if not GALLERY_DIR.exists():
        return []

    return sorted(
        [path for path in GALLERY_DIR.iterdir() if path.is_file() and path.suffix in IMAGE_EXTENSIONS],
        key=lambda path: path.name.lower(),
    )


def public_path(path):
    return "/" + path.relative_to(ROOT).as_posix().replace("#", "%23")


def update_gallery_page():
    html = GALLERY_PAGE.read_text(encoding="utf-8")
    images = gallery_images()
    image_html = "\n".join(
        f'          <img src="{public_path(path)}" alt="{path.stem}">'
        for path in images
    )

    start_marker = '        <div class="gallery-grid" aria-label="Gallery images">\n'
    end_marker = '        </div>\n      </section>'
    start = html.find(start_marker)
    end = html.find(end_marker, start)
    if start == -1 or end == -1:
        fail("Could not find gallery grid in gallery/index.html")

    updated = html[: start + len(start_marker)] + image_html + "\n" + html[end:]
    GALLERY_PAGE.write_text(updated, encoding="utf-8")
    return len(images)


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    projects = build_projects()
    events = build_events(projects)
    write_json(WORKS_JSON, {"works": projects})
    write_json(EVENTS_JSON, {"events": events})
    image_count = update_gallery_page()

    print(f"Updated {len(projects)} project(s).")
    print(f"Updated {len(events)} event(s).")
    print(f"Updated {image_count} gallery image(s).")
    print("Done.")


if __name__ == "__main__":
    main()

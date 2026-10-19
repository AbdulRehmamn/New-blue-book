"""Transactional crawl state and source-preserving exports."""
import csv
import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ["Company Name", "Contact Name", "Title", "Department", "Phone Number", "Extension", "Phone Type", "Email", "Company Phone", "Company Email", "Website", "City", "State", "County", "Postal Code", "Address", "Profile URL", "Contact Source URL", "Email Source URLs", "Extraction Method", "Missing Fields", "Evidence", "Collected UTC"]


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.last_excel_path = self.folder / "contacts.xlsx"
        self.last_csv_path = self.folder / "contacts.csv"
        self.db = sqlite3.connect(self.folder / "progress.sqlite3", timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS queue(url TEXT PRIMARY KEY,kind TEXT,status TEXT DEFAULT 'pending',attempts INTEGER DEFAULT 0,error TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS companies(id TEXT PRIMARY KEY,payload TEXT,updated TEXT);
        CREATE TABLE IF NOT EXISTS pages(url TEXT PRIMARY KEY,status TEXT,notes TEXT,updated TEXT);
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT);
        ''')
        self.db.execute("UPDATE queue SET status='pending' WHERE status='running'")
        self.db.commit()

    def enqueue(self, url, kind):
        self.db.execute("INSERT OR IGNORE INTO queue(url,kind) VALUES(?,?)", (url, kind))

    def pop(self):
        row = self.db.execute("SELECT * FROM queue WHERE status='pending' ORDER BY CASE kind WHEN 'profile' THEN 0 WHEN 'contacts' THEN 1 ELSE 2 END,rowid LIMIT 1").fetchone()
        if row:
            self.db.execute("UPDATE queue SET status='running',attempts=attempts+1 WHERE url=?", (row["url"],))
            self.db.commit()
        return dict(row) if row else None

    def finish(self, url, status, notes=""):
        self.db.execute("UPDATE queue SET status=?,error=? WHERE url=?", (status, notes, url))
        self.db.execute("INSERT OR REPLACE INTO pages VALUES(?,?,?,?)", (url, status, notes, utc()))
        self.db.commit()

    def retry_errors(self):
        self.db.execute("UPDATE queue SET status='pending' WHERE status IN ('error','blocked','empty') OR kind='listing'")
        self.db.commit()

    def save_company(self, data):
        old = self.db.execute("SELECT payload FROM companies WHERE id=?", (data["company_id"],)).fetchone()
        if old:
            original = json.loads(old[0])
            for key in ("phones", "emails", "email_sources"):
                data[key] = original.get(key, []) + [p for p in data.get(key, []) if p not in original.get(key, [])]
            def person_key(person):
                return person["name"].casefold() if person["name"] else "unnamed:" + json.dumps([person.get("phones", []), person.get("emails", [])], sort_keys=True)
            people = {person_key(c): c for c in original.get("contacts", [])}
            for person in data.get("contacts", []):
                key = person_key(person)
                if key in people:
                    previous = people[key]
                    for field in ("phones", "emails"):
                        person[field] = previous.get(field, []) + [p for p in person.get(field, []) if p not in previous.get(field, [])]
                    person["title"] = person.get("title") or previous.get("title", "")
                people[key] = person
            data["contacts"] = list(people.values())
            if data.get("method") == "listing_card" and original.get("method") != "listing_card":
                for key in ("company_name", "method", "evidence", "source_url", "website", "city", "state", "county", "postal_code", "address"):
                    data[key] = original.get(key) or data.get(key, "")
            for key in ("website", "city", "state", "county", "postal_code", "address"):
                data[key] = data.get(key) or original.get(key, "")
            if "/locations-contacts/" in original.get("source_url", "") and "/locations-contacts/" not in data.get("source_url", ""):
                data["source_url"] = original["source_url"]
        self.db.execute("INSERT OR REPLACE INTO companies VALUES(?,?,?)", (data["company_id"], json.dumps(data, ensure_ascii=False), utc()))
        self.db.commit()

    def get_company(self, company_id):
        row = self.db.execute("SELECT payload FROM companies WHERE id=?", (company_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def stats(self):
        result = {r[0]: r[1] for r in self.db.execute("SELECT status,count(*) FROM queue GROUP BY status")}
        result["companies"] = self.db.execute("SELECT count(*) FROM companies").fetchone()[0]
        return result

    def _raw_rows(self):
        for record in self.db.execute("SELECT payload,updated FROM companies ORDER BY rowid"):
            c = json.loads(record[0])
            base = {"_company_id": c["company_id"], "Company Name": c["company_name"], "Company Phone": "; ".join(p["phone"] + (" x" + p["extension"] if p["extension"] else "") for p in c["phones"] if p["kind"] != "Fax"), "Company Email": "; ".join(c["emails"]), "Website": c["website"], "City": c["city"], "State": c["state"], "County": c["county"], "Postal Code": c["postal_code"], "Address": c["address"], "Profile URL": c["profile_url"], "Contact Source URL": c["source_url"], "Email Source URLs": "; ".join(c["email_sources"]), "Collected UTC": record[1]}
            # Company phones have independent rows; no false person-to-switchboard assignment.
            entries = [(None, p) for p in c["phones"]]
            for person in c["contacts"]:
                entries.extend((person, p) for p in person["phones"] or [None])
            if not entries:
                entries = [(None, None)]
            for person, phone in entries:
                row = dict(base)
                row.update({"Contact Name": person["name"] if person else "", "Title": person["title"] if person else "", "Department": person["department"] if person else "", "Phone Number": phone["phone"] if phone else "", "Extension": phone["extension"] if phone else "", "Phone Type": phone["kind"] if phone else "", "Email": "; ".join(person["emails"]) if person else "; ".join(c["emails"]), "Extraction Method": person["method"] if person else c.get("method", "company_section"), "Evidence": person["evidence"] if person else c.get("evidence", "Company-level contact; no named owner inferred.")})
                row["Missing Fields"] = "; ".join(k for k in ("Contact Name", "Phone Number", "Email") if not row[k])
                yield row

    @staticmethod
    def phone_key(number):
        digits = re.sub(r"\D", "", number)
        return digits[1:] if len(digits) == 11 and digits.startswith("1") else digits

    def _selected_rows(self):
        companies = {}
        for row in self._raw_rows():
            key = row.get("_company_id") or (row["Company Name"], row["Profile URL"])
            companies.setdefault(key, []).append(row)
        for entries in companies.values():
            main = {self.phone_key(r["Phone Number"]) for r in entries
                    if not r["Contact Name"] and r["Phone Type"] != "Fax" and r["Phone Number"]}
            users = {}
            for r in entries:
                if r["Contact Name"]:
                    users.setdefault(self.phone_key(r["Phone Number"]), set()).add(r["Contact Name"].casefold())
            def rank(r):
                key = self.phone_key(r["Phone Number"])
                if not key or r["Phone Type"] == "Fax":
                    return 99
                owner = bool(re.search(r"\b(?:owner|co-owner|founder|principal|president|CEO|chief executive)\b", r["Title"], re.I))
                direct = key not in main and len(users.get(key, set())) == 1
                if r["Contact Name"] and owner and direct:
                    return 0
                if r["Phone Type"] == "Mobile":
                    return 1
                if not r["Contact Name"]:
                    return 2
                return 3
            selected = dict(min(entries, key=rank))
            priority = rank(selected)
            if priority == 99:
                # No usable number: retain company information without a fax.
                selected = dict(entries[0])
                for field in ("Contact Name", "Title", "Department", "Phone Number", "Extension", "Phone Type"):
                    selected[field] = ""
                reason = "No published non-fax phone available."
            else:
                reason = ["Owner/executive contact number published separately from main/shared numbers.",
                          "Source explicitly labels this number as mobile/cell; carrier not independently verified.",
                          "Main company number (owner direct/mobile not available).",
                          "Published contact number (owner direct/mobile/main not available). "][priority]
            # Only one number is exposed; keep the complete source data in SQLite.
            selected["Company Phone"] = ""
            selected["Evidence"] = reason + " " + selected["Evidence"]
            yield selected

    def rows(self):
        """One row per dialable number, including across resumed/company records.

        Keep all published names and evidence without guessing a primary owner.
        Contacts without a number remain available as separate rows.
        """
        grouped = {}
        for row in self._selected_rows():
            number = row["Phone Number"]
            if not number:
                yield row
                continue
            digits = re.sub(r"\D", "", number)
            if len(digits) == 11 and digits.startswith("1"):
                digits = digits[1:]
            key = digits or number.strip()
            if key not in grouped:
                grouped[key] = {field: [] for field in FIELDS}
            values = grouped[key]
            for field in FIELDS:
                value = row.get(field, "")
                if value and value not in values[field] and field not in ("Phone Number", "Missing Fields"):
                    values[field].append(value)
            if not values["Phone Number"]:
                values["Phone Number"].append(number)
        for values in grouped.values():
            row = {field: " | ".join(items) for field, items in values.items()}
            row["Missing Fields"] = "; ".join(field for field in ("Contact Name", "Phone Number", "Email") if not row[field])
            yield row

    def snapshot(self, url, markup):
        folder = self.folder / "page_cache"
        folder.mkdir(exist_ok=True)
        key = hashlib.sha256(url.encode()).hexdigest()
        target = folder / (key + ".json")
        tmp = target.with_suffix(".tmp")
        tmp.write_text(json.dumps({"url": url, "html": markup}, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, target)

    def recover_cached_pages(self):
        from extractor import extract_company, extract_listing_companies, profile_root
        recovered = 0
        for path in sorted((self.folder / "page_cache").glob("*.json")):
            try:
                page = json.loads(path.read_text(encoding="utf-8"))
                if profile_root(page["url"]):
                    company = extract_company(page["html"], page["url"])
                    companies = [company] if company else []
                else:
                    companies = extract_listing_companies(page["html"], page["url"])
                for company in companies:
                    self.save_company(company.dictionary())
                    recovered += 1
            except (ValueError, KeyError, TypeError):
                continue
        return recovered

    def export(self):
        rows = list(self.rows())
        def safe(value):
            value = str(value or "")
            # Prevent CSV formula execution; keep phone cells as text in Excel.
            return "'" + value if value.startswith(("=", "+", "-", "@", "\t", "\r")) else value
        target = self.folder / "contacts.csv"
        tmp = target.with_suffix(".csv.tmp")
        with tmp.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows({k: safe(row.get(k, "")) for k in FIELDS} for row in rows)
        try:
            os.replace(tmp, target)
        except PermissionError:
            target = self.folder / f"contacts_saved_{datetime.now():%Y%m%d_%H%M%S_%f}.csv"
            os.replace(tmp, target)
        self.last_csv_path = target
        with (self.folder / "phones.txt.tmp").open("w", encoding="utf-8") as handle:
            numbers = sorted({r["Phone Number"] for r in rows if r["Phone Number"] and r["Phone Type"] != "Fax"})
            handle.write("\n".join(numbers) + ("\n" if numbers else ""))
        os.replace(self.folder / "phones.txt.tmp", self.folder / "phones.txt")
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            book = Workbook()
            sheet = book.active
            sheet.title = "Contacts"
            sheet.append(FIELDS)
            for row in rows:
                sheet.append([str(row.get(k, "")) for k in FIELDS])
                for cell in sheet[sheet.max_row]:
                    cell.data_type = "s"
                    cell.number_format = "@"
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
            for cell in sheet[1]:
                cell.fill = PatternFill("solid", fgColor="183B66")
                cell.font = Font(color="FFFFFF", bold=True)
            for column in sheet.columns:
                letter = column[0].column_letter
                sheet.column_dimensions[letter].width = min(55, max(18, len(str(column[0].value)) + 5))
            audit = book.create_sheet("Pages")
            audit.append(["URL", "Status", "Notes", "Updated UTC"])
            for item in self.db.execute("SELECT q.url,q.status,coalesce(nullif(q.error,''),p.notes,''),coalesce(p.updated,'') FROM queue q LEFT JOIN pages p ON p.url=q.url ORDER BY q.rowid"):
                audit.append(list(item))
                for cell in audit[audit.max_row]:
                    cell.data_type = "s"
            audit.freeze_panes = "A2"
            audit.auto_filter.ref = audit.dimensions
            audit.column_dimensions["A"].width = 80
            audit.column_dimensions["B"].width = 20
            audit.column_dimensions["C"].width = 80
            summary = book.create_sheet("Summary", 0 if not rows else 2)
            summary.append(["Export status", "Details"])
            summary.append(["Contact rows", len(rows)])
            summary.append(["Companies", self.stats().get("companies", 0)])
            summary.append(["Updated UTC", utc()])
            summary.append(["Result", "Collected contacts are on the Contacts sheet." if rows else "NO CONTACTS COLLECTED. Check Pages for access checks/errors, then Start / Resume with Retry enabled."])
            summary.append(["Listing data", "Rows marked listing_card contain published listing details; profile details may still need access."])
            summary.append(["Pending/blocked URLs", "See Pages. URLs without collected details are never presented as contacts."])
            for key, value in sorted(self.stats().items()):
                if key != "companies":
                    summary.append([key + " pages", value])
            summary.column_dimensions["A"].width = 25
            summary.column_dimensions["B"].width = 100
            for row in summary:
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")
            summary.row_dimensions[6].height = 32
            book.active = 0
            book.save(self.folder / "contacts.tmp.xlsx")
            target = self.folder / "contacts.xlsx"
            try:
                os.replace(self.folder / "contacts.tmp.xlsx", target)
            except PermissionError:
                # Excel on Windows locks an open workbook. Keep the new data in
                # a separate workbook instead of leaving only a stale export.
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                target = self.folder / f"contacts_saved_{stamp}.xlsx"
                os.replace(self.folder / "contacts.tmp.xlsx", target)
            self.last_excel_path = target
        except PermissionError:
            raise PermissionError("Could not write the Excel workbook. Check folder permissions, then export again. CSV and database are already saved.")
        with (self.folder / "run_summary.json").open("w", encoding="utf-8") as handle:
            json.dump({"updated_utc": utc(), "rows": len(rows), "excel_file": self.last_excel_path.name, "csv_file": self.last_csv_path.name, "status": "contacts_saved" if rows else "no_contacts_collected", **self.stats()}, handle, indent=2)
        return len(rows)

    def close(self):
        self.db.close()


def job_folder(root, seeds, broad, enrich):
    identity = json.dumps({"seeds": sorted(set(seeds)), "directory_discovery": broad, "company_website": enrich}, sort_keys=True)
    digest = hashlib.sha256(identity.encode()).hexdigest()[:12]
    folder = Path(root) / ("job_" + digest)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "job.json").write_text(identity, encoding="utf-8")
    return folder

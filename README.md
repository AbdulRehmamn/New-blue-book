# Blue Book Contact Scraper

A Python desktop tool for Windows 10/11 that follows Blue Book search-result pages, opens company profiles and their **Locations & Key Contacts** pages, and exports published business contacts.

## Start on Windows

1. Extract the entire ZIP into a normal writable folder, such as `Documents\BlueBook_Contact_Scraper`. Do not run it from inside the ZIP.
2. Double-click **start.bat**. It creates a local Python environment, installs the required packages and Chromium, then launches the desktop app. The first launch needs internet and may take several minutes. If Python is missing, it tries the official Python 3.12 package through Windows Package Manager; if unavailable, it shows the manual installation link.
3. Click **Open Blue Book**. Search for a trade and location in the visible browser.
4. Click **Copy browser URL**, or paste one or more Blue Book search-results, directory or company-profile URLs into the box, one per line.
5. Click **Start / Resume**. Click **Open exports** to find results.

The browser stays visible. Do not navigate the scraper tab while it is running. Use **Stop & Save** before making another search.

## What it collects

- Company names and company-level phone numbers.
- Published named contacts, titles, departments and the phone/email details shown with that person.
- Public company emails, with optional checks of the linked official website and up to four contact/about/team pages.
- City, state, postal code, street address and county when explicitly published in supported page content.
- Company profile URLs, source URLs, extraction method, evidence and collection time.

Company phone numbers and named-contact phone numbers are kept separate. A company switchboard is never automatically labeled as the owner's personal number. Phone values are normalized, extensions are separate, and fax numbers are labeled. The tool does not claim a number is mobile without carrier verification.

## Export files

Each job has a folder under `output\job_<id>\`:

| File | Contents |
| --- | --- |
| `contacts.xlsx` | Filterable Contacts sheet, complete queue audit in Pages, and Summary (shown first when empty) |
| `contacts.csv` | UTF-8 CSV with one phone number per row; contacts without numbers are retained |
| `phones.txt` | Unique non-fax phone numbers, one per line |
| `progress.sqlite3` | Persistent queue and contact database |
| `run_summary.json` | Page status counts and export timestamp |
| `run.log` | Progress and error messages |
| `job.json` | Selected seed URLs and crawl options |

**Read UPDATE_READ_FIRST.txt for the current export/layout recovery fix and installation steps.**

The **Keep Excel updated after every completed page** option is enabled by default. With it enabled, Excel updates after each queue page; turn it off to use the previous every-10-pages interval. **Stop & Save always exports all contacts collected so far**, regardless of this option. Wait for the status to say **Stopped — saved … contact rows**, then click **Open exports**. For example, if you stop after 500 of 1,000 pages, the contacts extracted from those 500 completed pages are exported; unvisited queued URLs are retained for resume. The database is committed after each extracted company and queue page. If `contacts.xlsx` is open in Excel and cannot be replaced, the latest export is saved as `contacts_saved_<timestamp>.xlsx` in the same folder; its exact name appears in the log and final status. Closing Excel lets future exports update `contacts.xlsx` normally. CSV cells beginning with formula characters are prefixed with an apostrophe to prevent formula execution; `phones.txt` has plain numbers and XLSX phone cells are text.

## Pagination and coverage

The tool follows actual observed pagination links, including Next, numeric pages and Last. It also handles common JavaScript-only Next/Load more buttons and lazy-loaded cards. It does not guess that a URL uses `page=2`, and it does not stop after only the first results page. Repeated company profiles and repeated pages are deduplicated.

Use a search-results URL for a specific trade/location. Multiple seed URLs are supported. **Discover linked directories/categories** broadens the crawl to supported directory/category links; using the homepage automatically enables this option. A broad homepage crawl can be very large. The tool cannot guarantee discovery of every page on the entire Blue Book site: unlinked, gated, unsupported search widgets or changed layouts can prevent discovery. It records blocked/error pages for review rather than reporting complete coverage.

**Pages per session** counts queued listing/profile/contact pages. A value of `0` means no session cap. JavaScript pagination may make several browser requests while processing a single listing queue item; it stops after 5,000 button steps with a reviewable error. Lazy scrolling is bounded to 150 steps per listing. The app logs discovered queue exhaustion, not a claim that every company on the website was collected.

## Pause, stop and resume

- **Pause / Resume** controls the running crawl.
- **Stop & Save** preserves the queue and exports collected contacts, including data saved before an interrupted company-website check. The final status confirms the saved row count and Excel filename. An in-flight navigation can take up to 45 seconds to return.
- Rerun **Start / Resume** with the same seed URLs and directory/website options to resume the same job. Changing those options or URLs creates a separate job, keeping old results intact.
- **Retry blocked and failed pages** requeues them at the start of a run. Completed company pages are not unnecessarily reprocessed. Listing pages refresh when Retry is checked, to recover visible card data from older runs.
- An interrupted JavaScript pagination sequence reopens its listing and discovers from there; already saved profiles remain deduplicated.
- **Export saved data** can export an existing job without rerunning the crawl.

## Access checks and blank fields

Blue Book can return a verification screen, sign-in requirement, rate limit or 403. The scraper pauses with the visible browser open. If access is available through the site's normal controls, click **Continue after access check**; otherwise use **Stop & Save** and retry later. The tool does not solve CAPTCHAs, rotate proxies or bypass access controls. A persistent browser profile retains site session data on your computer; keep `browser_profile` private and do not share that folder.

Names and emails are exported only when published and recognized. Missing data remains blank and is identified in **Missing Fields**. Company-site emails go into **Company Email**; they are not attributed to an individual unless the contact section explicitly associates them. Emails are not guessed or mailbox-verified. County is not inferred from city or ZIP. Review the evidence/source columns for important contacts.

## Latest update: save partial results

To update an existing installation, close the scraper and copy `app.py`, `crawler.py`, `extractor.py`, `storage.py`, `requirements.txt`, and `start.bat` from this package into your existing scraper folder, replacing those three files. Keep your existing `output` folder to retain previous jobs. Run `start.bat` normally.

## Validation and limits

The included automated tests cover extraction, separate person/phone associations, fax handling, missing fields, structured Person data, observed-link pagination, deduplication, job isolation, durable resume and exports. Crawler tests use synthetic HTML and an in-memory page adapter to verify a three-page crawl and queue behavior. Run them with:

```console
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

During creation, live Blue Book access from the development environment returned HTTP 403, and the local Chromium download was unavailable. Consequently the current production HTML selectors, real browser behavior, complete site coverage and Windows installer execution could not be verified end to end. This package contains the implementation and passing local tests; a first small run on your Windows computer is required to verify live-site compatibility. Review blocked/errors in the Pages sheet.

## Other platforms / command line

Python 3.10+ and Tkinter are required. Windows is the primary target.

```console
python -m venv .venv
python -m pip install -r requirements.txt
python -m playwright install chromium
python app.py
```

On Linux, install your distribution's Tkinter and Playwright system dependencies if required. Activate the environment or use its Python executable before these commands. No paid API key or external contact database is required.

## Recovery update

Company identities no longer require an h1. Styled company names, structured Organization data and company-specific metadata are supported. Visible listing-card details are committed/exported before profile requests; rows marked `listing_card` contain only published listing details. The audit includes pending URLs even if no contacts could be collected. An empty workbook opens on Summary, explaining the zero count.

The minimum request delay is 5 seconds. Temporary navigation/server failures get at most one automatic retry. Rate limiting triggers an interruptible cooldown and a higher delay; three consecutive failures pause requests until you inspect the browser and continue. Already open accessible pages are reused. Accessible HTML snapshots under `page_cache` allow offline re-extraction during resume/export after selector updates. Snapshots stay local and should be kept private. Old runs without snapshots cannot recover content that was never collected.

The export button can request a save while running (at the next browser checkpoint). CSV and Excel exports use alternate filenames when the standard files are open/locked. See `run_summary.json` and the log for the current export filename.

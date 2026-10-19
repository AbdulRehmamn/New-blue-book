"""One visible browser, a durable queue, and explicit interruption handling."""
from __future__ import annotations

import hashlib
import ipaddress
import json
import queue
import re
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit, urljoin

from bs4 import BeautifulSoup
from extractor import canonical, discover, extract_company, emails, content_soup, profile_root, is_bluebook, PROFILE, access_problem, extract_listing_companies, company_name
from storage import Store, job_folder

class Stopped(Exception):
    pass


def public_web_url(url):
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password:
            return False
        host = parsed.hostname or ""
        if not host or host == "localhost" or host.endswith((".local", ".localhost", ".internal")):
            return False
        try:
            if not ipaddress.ip_address(host).is_global:
                return False
        except ValueError:
            pass
        return True
    except ValueError:
        return False


class Worker(threading.Thread):
    def __init__(self, events, root):
        super().__init__(daemon=True)
        self.events = events
        self.root = Path(root)
        self.commands = queue.Queue()
        self.stop_event = threading.Event()
        self.resume_event = threading.Event()
        self.export_event = threading.Event()
        self.pause_event = threading.Event()
        self.context = None
        self.page = None
        self.store = None
        self.last_request = 0
        self.effective_delay = 5
        self.consecutive_failures = 0

    def emit(self, kind, value):
        self.events.put((kind, value))

    def log(self, message):
        self.emit("log", message)

    def check(self):
        if self.export_event.is_set() and self.store:
            self.export_event.clear()
            self.save_exports()
        if self.stop_event.is_set():
            raise Stopped()
        if self.pause_event.is_set():
            self.emit("status", "Paused. Click Resume to continue.")
            while self.pause_event.is_set():
                if self.stop_event.wait(.2):
                    raise Stopped()
            self.emit("status", "Running")

    def wait_manual(self, reason):
        self.resume_event.clear()
        self.emit("status", reason)
        self.log(reason)
        self.emit("attention", reason)
        while not self.resume_event.wait(.2):
            self.check()
        self.check()

    def pace(self, delay):
        remaining = delay - (time.monotonic() - self.last_request)
        if remaining > 0:
            if self.stop_event.wait(remaining):
                raise Stopped()
        self.check()
        self.last_request = time.monotonic()

    def route(self, route):
        url = route.request.url
        if urlsplit(url).scheme in {"http", "https"} and not public_web_url(url):
            route.abort()
        elif route.request.resource_type in {"media", "font"}:
            route.abort()
        else:
            route.continue_()

    def run(self):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as playwright:
                self.context = playwright.chromium.launch_persistent_context(
                    str(self.root / "browser_profile"), headless=False,
                    viewport={"width": 1280, "height": 850}, accept_downloads=False)
                self.context.route("**/*", self.route)
                self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
                self.emit("ready", True)
                while True:
                    command, payload = self.commands.get()
                    if command == "quit":
                        break
                    try:
                        if command == "browse":
                            self.page.goto("https://www.thebluebook.com/", wait_until="domcontentloaded", timeout=45000)
                            self.log("Search Blue Book in the browser, then use Copy browser URL.")
                        elif command == "url":
                            # Use the active/newest public Blue Book page if the site opened another tab.
                            candidates = [p for p in self.context.pages if is_bluebook(p.url)]
                            if candidates:
                                self.page = candidates[-1]
                            self.emit("url", self.page.url)
                        elif command == "crawl":
                            self.crawl(payload)
                        elif command == "export":
                            with_folder = Store(payload)
                            try:
                                n = with_folder.export()
                                self.log(f"Exported {n} rows to {payload}")
                            finally:
                                with_folder.close()
                    except Stopped:
                        self.log("Stopped. Saved progress; Start / Resume continues the same job.")
                    except Exception as exc:
                        self.log(f"{type(exc).__name__}: {exc}")
                        self.emit("attention", str(exc))
                    finally:
                        if command == "crawl":
                            if self.store:
                                self.store.close()
                                self.store = None
                self.context.close()
        except Exception as exc:
            self.log(f"Browser could not start: {exc}")
            self.log("Run start.bat to install Chromium. If already running, close the other scraper window.")
            self.emit("failed", str(exc))

    def load(self, url, delay):
        """Retry temporary failures once; leave genuine access checks to normal site controls."""
        if canonical(self.page.url) == canonical(url):
            markup = self.page.content()
            if not access_problem(markup) and (
                extract_company(markup, self.page.url) if profile_root(url)
                else discover(markup, self.page.url)):
                self.check()
                return markup
        status, response = 200, None
        for attempt in range(2):
            self.pace(max(delay, self.effective_delay))
            try:
                response = self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
                status = response.status if response else 200
            except Exception:
                self.check()
                # A navigation timeout can still leave a fully usable document.
                current = canonical(self.page.url)
                same_page = current == canonical(url) or (profile_root(url) and profile_root(current) == profile_root(url))
                markup = self.page.content() if same_page else ""
                if not markup or access_problem(markup) or not (
                    extract_company(markup, self.page.url) if profile_root(url)
                    else discover(markup, self.page.url)):
                    if attempt:
                        raise
                    self.log("Navigation failed; waiting 10 seconds before one retry.")
                    if self.stop_event.wait(10):
                        raise Stopped()
                    continue
                status = 200
            self.check()
            self.page.wait_for_timeout(1200)
            markup = self.page.content()
            reason = access_problem(markup, status)
            if status == 429 and attempt == 0:
                header = (response.headers if response else {}).get("retry-after", "")
                try:
                    cooldown = min(300, max(30, float(header)))
                except ValueError:
                    cooldown = 60
                self.log(f"Rate limited: waiting {cooldown:g} seconds before one retry. Stop & Save remains available.")
                self.emit("status", f"Rate limit cooldown: {cooldown:g} seconds. Stop & Save is available.")
                self.effective_delay = min(60, max(self.effective_delay * 2, delay))
                if self.stop_event.wait(cooldown):
                    raise Stopped()
                continue
            if status >= 500:
                if attempt == 0:
                    if self.stop_event.wait(10):
                        raise Stopped()
                    continue
                raise RuntimeError(f"Server HTTP {status}; kept for retry")
            if reason:
                # Retain any earlier contacts before waiting for the user.
                self.save_exports()
                self.wait_manual(reason + ". Use the site's normal browser controls, then click Continue after access check. Stop & Save preserves collected results.")
                same_company = not profile_root(url) or profile_root(self.page.url) == profile_root(url)
                if not same_company or not is_bluebook(self.page.url):
                    raise PermissionError("Browser left the requested company/site; URL retained for retry")
                markup = self.page.content()
                if access_problem(markup):
                    raise PermissionError("Access is still restricted. URL retained for retry; no contact data was fabricated.")
                return markup
            if status >= 400:
                raise RuntimeError(f"HTTP {status}; kept for retry")
            # Allow asynchronously rendered identity/cards to appear, without relying on h1.
            for _ in range(12):
                self.check()
                if (extract_company(markup, self.page.url) if profile_root(url)
                    else discover(markup, self.page.url)):
                    break
                self.page.wait_for_timeout(500)
                markup = self.page.content()
                reason = access_problem(markup)
                if reason:
                    raise PermissionError(reason)
            return markup
        raise RuntimeError("Temporary navigation failure; kept for retry")

    def expand_public_details(self):
        # Only click visible phone/email disclosure buttons; never forms or send buttons.
        buttons = self.page.get_by_text(re.compile(r"^View\s+(?:Alt\s+)?(?:Phone|Email|Fax)$", re.I))
        count = min(buttons.count(), 100)
        for i in range(count):
            self.check()
            try:
                button = buttons.nth(i)
                if not button.is_visible():
                    continue
                tag = button.evaluate("e => ({tag:e.tagName, href:e.getAttribute('href'), type:e.getAttribute('type')})")
                href = tag.get("href") or ""
                if href.startswith(("tel:", "mailto:")) or (href and not href.startswith(("#", "javascript:"))):
                    continue
                if tag["type"] == "submit":
                    continue
                button.click(timeout=2000, no_wait_after=True)
            except Exception:
                continue
        self.page.wait_for_timeout(250)

    def listing(self, markup, url, broad, delay):
        self.add_links(markup, url, broad)
        # Scroll loads cards on lazy directories; stop when neither profiles nor height grow.
        seen, stable = set(), 0
        for _ in range(150):
            self.check()
            markup = self.page.content()
            links = discover(markup, self.page.url, broad)
            ids = {profile_root(u) for u, kind in links if kind == "profile"}
            new = ids - seen
            stable = 0 if new else stable + 1
            seen |= ids
            self.add_links(markup, self.page.url, broad)
            if stable >= 3:
                break
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(900)
        # Support genuine JS-only Next/Load more controls as well as href pagination.
        fingerprints = set()
        for page_index in range(5000):
            self.check()
            current_markup = self.page.content()
            self.add_links(current_markup, self.page.url, broad)
            ids = sorted(u for u, kind in discover(current_markup, self.page.url) if kind == "profile")
            fingerprint = hashlib.sha256(json.dumps(ids).encode()).hexdigest()
            if not ids or fingerprint in fingerprints:
                break
            fingerprints.add(fingerprint)
            locator = self.page.locator("button, a[role=button], input[type=button]").filter(has_text=re.compile(r"^\s*(?:next(?:\s+page)?|load\s+more(?:\s+results)?|show\s+more)\s*[›»→]?\s*$", re.I))
            if not locator.count():
                # Anchors with href have already been queued; only handle no-href JS Next.
                locator = self.page.locator('a:not([href]), a[href="#"], a[href^="javascript:"]').filter(has_text=re.compile(r"^\s*next\s*[›»→]?\s*$", re.I))
            button = next((p for p in locator.all() if p.is_visible() and p.is_enabled() and p.get_attribute("aria-disabled") != "true"), None)
            if button is None:
                break
            self.pace(max(delay, self.effective_delay))
            button.click(timeout=10000)
            self.page.wait_for_timeout(1500)
            if page_index == 4999:
                raise RuntimeError("JS pagination reached 5,000 steps. Resume from current results URL.")

    def add_links(self, markup, url, broad):
        changed = False
        for company in extract_listing_companies(markup, url):
            data = company.dictionary()
            old = self.store.get_company(data["company_id"])
            if old is None or any(p not in old.get("phones", []) for p in data["phones"]) or any(e not in old.get("emails", []) for e in data["emails"]):
                self.store.save_company(data)
                changed = True
        if changed:
            self.store.snapshot(url, markup)
            self.emit("stats", self.store.stats())
            self.save_exports()
        for target, kind in discover(markup, url, broad):
            if kind == "profile":
                self.store.enqueue(target, "profile")
                self.store.enqueue(target + "locations-contacts/", "contacts")
            else:
                self.store.enqueue(target, kind)
        self.store.db.commit()

    def enrich(self, data, delay):
        website = data.get("website", "")
        if not website or not public_web_url(website):
            return
        host = urlsplit(website).hostname
        page = self.context.new_page()
        visited, pending = set(), [website]
        try:
            while pending and len(visited) < 5:
                self.check()
                target = pending.pop(0)
                if target in visited:
                    continue
                visited.add(target)
                self.pace(max(delay, self.effective_delay))
                try:
                    response = page.goto(target, wait_until="domcontentloaded", timeout=25000)
                    if response and response.status >= 400:
                        continue
                    final = urlsplit(page.url).hostname
                    if not public_web_url(page.url) or (final or "").removeprefix("www.") != (host or "").removeprefix("www."):
                        continue
                    title = page.title().lower()
                    if any(v in title for v in ("just a moment", "access denied", "access verification")):
                        continue
                    # Company site header/footer often contain its own correct business email.
                    soup = BeautifulSoup(page.content(), "html.parser")
                    for element in soup.select("script, style, noscript, form"):
                        element.decompose()
                    values = emails(soup.get_text(" "))
                    for a in soup.select('a[href^="mailto:"]'):
                        values.extend(emails(a["href"]))
                    if values:
                        data["emails"] = sorted(set(data["emails"] + values))
                        data["email_sources"] = sorted(set(data["email_sources"] + [page.url]))
                    for a in soup.select("a[href]"):
                        link = canonical(a["href"], page.url)
                        if link and public_web_url(link) and (urlsplit(link).hostname or "").removeprefix("www.") == (host or "").removeprefix("www."):
                            if re.search(r"contact|about|team", a.get_text(" ") + " " + urlsplit(link).path, re.I) and link not in visited and link not in pending:
                                pending.append(link)
                except Exception as exc:
                    self.log(f"Company website skipped: {type(exc).__name__}")
        finally:
            page.close()

    def save_exports(self, final=False):
        try:
            count = self.store.export()
            path = self.store.last_excel_path
            self.emit("exported", str(path))
            self.log(f"Saved {count} contact rows to {path}")
            if final:
                if count:
                    result = f"{'Stopped' if self.stop_event.is_set() else 'Finished'} — saved {count} contact rows to {path.name}."
                else:
                    result = "No contacts collected. Open the Summary / Pages sheets to review failures, then Resume with Retry enabled."
                self.emit("finished", result)
        except Exception as exc:
            self.log(f"Export issue: {exc}. Database remains saved; use Export saved data to retry.")
            if final:
                self.emit("finished", "Stopped / finished. Excel export needs attention; see the log. Collected data is saved in the database.")

    def crawl(self, options):
        try:
            self._crawl(options)
        finally:
            # Also runs on Stop, pause/access-check interruption, and unexpected errors.
            # Keep this inside crawl so no caller can skip the final partial export.
            if self.store:
                self.save_exports(final=True)
            else:
                self.emit("finished", "Could not start this job. See the log.")

    def _crawl(self, options):
        seeds = sorted(set(canonical(u) for u in options["seeds"] if u.strip()))
        if not seeds or not all(is_bluebook(u) for u in seeds):
            raise ValueError("Paste one or more Blue Book results/profile URLs, one per line.")
        folder = job_folder(self.root / "output", seeds, options["broad"], options["enrich"])
        self.store = Store(folder)
        self.emit("folder", str(folder))
        self.effective_delay = max(5, options["delay"])
        self.consecutive_failures = 0
        recovered = self.store.recover_cached_pages()
        if recovered:
            self.log(f"Recovered {recovered} company records from previously saved page content.")
        if options["retry"]:
            self.store.retry_errors()
        for url in seeds:
            self.store.enqueue(url, "profile" if profile_root(url) else "listing")
            root = profile_root(url)
            if root:
                self.store.enqueue(root + "locations-contacts/", "contacts")
        self.store.db.commit()
        self.log(f"Job folder: {folder}")
        count = 0
        while options["limit"] == 0 or count < options["limit"]:
            self.check()
            item = self.store.pop()
            if not item:
                break
            url, kind = item["url"], item["kind"]
            self.log(f"[{count + 1}] {kind}: {url}")
            self.emit("status", f"Opening {kind} page…")
            try:
                markup = self.load(url, options["delay"])
                self.store.snapshot(self.page.url, markup)
                if kind == "listing":
                    self.listing(markup, url, options["broad"], options["delay"])
                else:
                    if profile_root(self.page.url) != profile_root(url):
                        raise RuntimeError("Redirect left the requested company profile")
                    self.expand_public_details()
                    markup = self.page.content()
                    self.store.snapshot(self.page.url, markup)
                    company = extract_company(markup, self.page.url)
                    if company is None:
                        raise ValueError("Company identity was not recognized. Page content saved in page_cache for recovery; see Pages audit.")
                    data = company.dictionary()
                    self.store.save_company(data)
                    # Enrich once after the home profile; merged record retains all contacts.
                    if kind == "profile" and options["enrich"] and data["website"]:
                        data = self.store.get_company(data["company_id"])
                        try:
                            self.enrich(data, options["delay"])
                        finally:
                            # Preserve emails collected before Stop interrupted enrichment.
                            self.store.save_company(data)
                if kind == "listing" and not discover(self.page.content(), self.page.url, options["broad"]):
                    raise ValueError("No profile/pagination links found on this listing. Check the browser URL or access state.")
                self.store.finish(url, "done")
                self.consecutive_failures = 0
            except Stopped:
                self.store.finish(url, "pending", "Stopped before page completed")
                raise
            except PermissionError as exc:
                self.store.finish(url, "blocked", str(exc))
                self.log(f"Blocked: {exc}")
                self.consecutive_failures += 1
            except Exception as exc:
                self.store.finish(url, "error", str(exc))
                self.log(f"Kept for retry: {type(exc).__name__}: {exc}")
                self.consecutive_failures += 1
            if self.consecutive_failures >= 3 and self.store.stats().get("pending", 0) and (not options["limit"] or count + 1 < options["limit"]):
                self.save_exports()
                self.effective_delay = min(60, self.effective_delay * 2)
                self.wait_manual("Three pages failed consecutively. Crawl paused to avoid repeated failed requests. Inspect the browser; click Continue after access check when ready, or Stop & Save.")
                self.consecutive_failures = 0
            count += 1
            self.emit("stats", self.store.stats())
            if options.get("autosave", True) or count % 10 == 0:
                self.save_exports()
        if options["limit"] and count >= options["limit"]:
            self.log("Session page limit reached. Resume continues pending URLs; set limit 0 for no session cap.")
        stats = self.store.stats()
        if not stats.get("pending"):
            self.log("Discovered queue exhausted. Review blocked/error pages and retry them if needed.")

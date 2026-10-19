"""Public Blue Book HTML extraction. No email guessing or hidden API calls."""
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field, asdict
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode, unquote

from bs4 import BeautifulSoup
import phonenumbers

PROFILE = re.compile(r"(/iProView/\d+/[^/]+/[^/]+/)", re.I)
EMAIL = re.compile(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9-]+(?:\.[A-Z0-9-]+)+", re.I)
PHONE = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?(?:\([2-9]\d{2}\)|[2-9]\d{2})[ .-]?\d{3}[ .-]?\d{4}(?:\s*(?:ext\.?|x|extension)\s*\d{1,7})?(?!\d)", re.I)
VENDOR_PHONES = {"+18887201710", "+18004312584"}
GROUPS = re.compile(r"^(?:Owners,.*|Principals.*|Senior Executives|Estimating,.*|Purchasing(?: & Preconstruction)?|Preconstruction|Business Development,.*|Marketing & Sales|Operations(?: Team| Staff)?|Other Contacts|Key Contacts|Contacts)$", re.I)
ROLE = re.compile(r"owner|president|pres\.?|ceo|cfo|coo|cto|manager|estimator|director|founder|partner|secretary|treasurer|superintendent|sales|vice|principal|engineer|coordinator|administrator|executive|purchasing|project|office|estimating", re.I)
END_MARKERS = {"find", "find by categories", "companies", "locations regions", "join our network", "request qualifications", "proview messaging", "request brochure"}


def clean(value):
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()


def canonical(url, base="https://www.thebluebook.com/"):
    # html.unescape would corrupt a literal query like '&region=3' into '®ion=3'.
    # BeautifulSoup already decodes HTML hrefs; only the explicit &amp; form is safe here.
    u = urlsplit(urljoin(base, url.replace("&amp;", "&")))
    if u.scheme not in ("http", "https") or u.username or u.password:
        return ""
    host = (u.hostname or "").lower()
    if host in ("thebluebook.com", "www.thebluebook.com"):
        host = "www.thebluebook.com"
    elif u.port:
        host += ":" + str(u.port)
    query = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in {"gclid", "fbclid"}]
    return urlunsplit((u.scheme, host, u.path or "/", urlencode(sorted(query)), ""))


def is_bluebook(url):
    return urlsplit(url).hostname in {"www.thebluebook.com", "thebluebook.com"}


def profile_root(url):
    match = PROFILE.search(urlsplit(url).path)
    return "https://www.thebluebook.com" + match.group(1) if match and is_bluebook(url) else ""


def emails(text):
    result = set()
    for value in EMAIL.findall(unquote(html.unescape(text))):
        value = value.strip(".,;:()<>[]").lower()
        if not value.endswith((".png", ".jpg", ".gif", ".webp", ".svg")) and not value.endswith("@thebluebook.com"):
            result.add(value)
    return sorted(result)


def phones(text):
    result = []
    for match in PHONE.finditer(text):
        try:
            number = phonenumbers.parse(match.group(), "US")
            if not phonenumbers.is_possible_number(number):
                continue
            normalized = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
            if normalized in VENDOR_PHONES:
                continue
            prefix = text[max(0, match.start() - 22):match.start()]
            kind = "Fax" if re.search(r"fax\W*$", prefix, re.I) else ("Mobile" if re.search(r"(?:mobile|cell(?:\s+phone)?|cellular)\W*$", prefix, re.I) else "Phone")
            row = {"phone": normalized, "extension": number.extension or "", "kind": kind}
            if row not in result:
                result.append(row)
        except phonenumbers.NumberParseException:
            pass
    return result


def plausible_name(text):
    text = clean(text)
    if not text or len(text) > 80 or text.lower() in {"unknown user", "not provided", "main location", "view phone", "contact us"}:
        return False
    if EMAIL.search(text) or PHONE.search(text) or GROUPS.search(text) or ROLE.search(text):
        return False
    if any(c.isdigit() for c in text) or re.search(r"\b(inc|llc|corp|company|construction|website|phone|fax|email|annual|location|qual|brochure|message|view|request)\b", text, re.I):
        return False
    words = text.split()
    return 2 <= len(words) <= 6 and all(re.fullmatch(r"[A-Za-zÀ-ž][A-Za-zÀ-ž.'’\-]*", w) for w in words)


def content_soup(markup):
    soup = BeautifulSoup(markup, "html.parser")
    # These elements are shared navigation, request forms, or unrelated dialogs.
    for tag in soup.select("script, style, noscript, header, footer, nav, form, [role=dialog], .modal, #footer, #header"):
        tag.decompose()
    for a in soup.select('a[href^="mailto:"]'):
        values = emails(a["href"])
        if values and not emails(a.get_text(" ")):
            a.append(" " + "; ".join(values))
    return soup


def lines_in(soup):
    lines = [clean(t) for t in soup.get_text("\n").splitlines() if clean(t)]
    # Header/title appears before the company contact section. Cut global menus.
    for i, line in enumerate(lines):
        if i > 3 and line.lower() in END_MARKERS:
            return lines[:i]
    return lines


@dataclass
class Contact:
    name: str = ""
    title: str = ""
    department: str = ""
    phones: list = field(default_factory=list)
    emails: list = field(default_factory=list)
    evidence: str = ""
    method: str = "contact_section"


@dataclass
class Company:
    company_id: str
    company_name: str
    profile_url: str
    source_url: str
    website: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    county: str = ""
    address: str = ""
    phones: list = field(default_factory=list)
    emails: list = field(default_factory=list)
    contacts: list = field(default_factory=list)
    email_sources: list = field(default_factory=list)
    method: str = "profile_page"
    evidence: str = "Published company section; no named owner inferred."

    def dictionary(self):
        return asdict(self)


def structured_people(soup):
    result = []
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            tree = json.loads(script.string or script.get_text())
        except (ValueError, TypeError):
            continue
        stack = [tree]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                types = node.get("@type", [])
                types = [types] if isinstance(types, str) else types
                if "Person" in types and plausible_name(node.get("name", "")):
                    result.append(Contact(clean(node["name"]), clean(node.get("jobTitle")),
                                          phones=phones(str(node.get("telephone", ""))),
                                          emails=emails(str(node.get("email", ""))), method="structured_person"))
                stack.extend(v for v in node.values() if isinstance(v, (list, dict)))
    return result


def parse_contacts(lines):
    start = next((i + 1 for i, t in enumerate(lines) if t.lower() == "key contacts"), None)
    if start is None:
        return []
    output, current, department = [], None, ""
    previous = ""
    for line in lines[start:]:
        if line.lower() in END_MARKERS or line.lower() == "locations":
            break
        if GROUPS.search(line) and not PHONE.search(line):
            if current:
                output.append(current)
                current = None
            department = line
            continue
        if line.lower() in {"unknown user", "not provided"}:
            if current:
                output.append(current)
            current = Contact(department=department, evidence=line, method="unnamed_contact")
            continue
        if plausible_name(line):
            if current:
                output.append(current)
            current = Contact(name=line, department=department, evidence=line)
            continue
        if current is None and (phones(line) or emails(line)):
            current = Contact(department=department, evidence="No published named contact", method="unnamed_contact")
        if current:
            current.evidence = (current.evidence + " | " + line)[:800]
            matched = phones(previous + " " + line) if re.fullmatch(r"(?:View\s+)?(?:Alt\s+)?(?:Phone|Fax|Mobile|Cell(?: Phone)?|Cellular)", previous, re.I) else phones(line)
            current.phones.extend(p for p in matched if p not in current.phones)
            current.emails = sorted(set(current.emails + emails(line)))
            if ROLE.search(line) and not PHONE.search(line) and not EMAIL.search(line):
                current.title = clean(current.title + " " + line)
        previous = line
    if current:
        output.append(current)
    # Repeated cards can repeat a person; merge only on normalized full name.
    merged = {}
    for contact in output:
        key = contact.name.casefold() if contact.name else "unnamed:" + json.dumps([contact.phones, contact.emails], sort_keys=True)
        if key not in merged:
            merged[key] = contact
        else:
            old = merged[key]
            old.title = old.title or contact.title
            old.department = old.department or contact.department
            old.phones.extend(p for p in contact.phones if p not in old.phones)
            old.emails = sorted(set(old.emails + contact.emails))
    return list(merged.values())


def access_problem(markup, status=200):
    """Recognize access/error screens without treating a normal contact page as one."""
    raw = BeautifulSoup(markup, "html.parser")
    title = clean(raw.title.get_text(" ") if raw.title else "").lower()
    for node in raw.select("script, style, noscript"):
        node.decompose()
    text = clean(raw.get_text(" ")).lower()
    if status == 429:
        return "Rate limit (HTTP 429)"
    if status in {401, 403}:
        return f"Access check (HTTP {status})"
    markers = ("access denied", "access verification", "just a moment", "403 error",
               "verify you are human", "verify that you are human", "checking your browser",
               "to continue to the requested proview", "unusual traffic", "automated requests",
               "request blocked", "please enable cookies", "enable javascript and cookies",
               "temporarily blocked", "too many requests", "pardon our interruption")
    if any(v in title for v in markers) or any(v in text[:6000] for v in markers):
        return "Website verification or access restriction"
    if re.search(r"^(?:sign in|log in|login)(?:\s*[|–—-]|$)", title):
        return "Sign-in required"
    return ""


def organization_nodes(raw):
    nodes = []
    for script in raw.select('script[type="application/ld+json"]'):
        try:
            stack = [json.loads(script.string or script.get_text())]
        except (ValueError, TypeError):
            continue
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                kinds = node.get("@type", [])
                kinds = [kinds] if isinstance(kinds, str) else kinds
                if any(k in {"Organization", "LocalBusiness", "GeneralContractor", "Electrician", "Plumber", "HomeAndConstructionBusiness"} for k in kinds):
                    nodes.append(node)
                stack.extend(v for v in node.values() if isinstance(v, (list, dict)))
    return nodes


def valid_company_name(value):
    value = clean(value)
    return bool(2 <= len(value) <= 200 and value.lower() not in {
        "access verification", "access denied", "403 error", "sign in", "log in",
        "locations", "key contacts", "locations & key contacts", "locations & contacts",
        "locations and contacts", "locations & contacts - proview", "company profile",
        "the blue book", "the blue book building & construction network", "home",
        "search results", "find companies", "contact us", "view proview", "proview",
        "view profile", "website", "phone", "view phone", "email", "view email"}
        and not any(t in value.lower() for t in ("verify you", "just a moment", "enable javascript", "access denied")))


def company_name(raw, soup):
    # Production profiles may use styled divs/h2 instead of an h1.
    for selector in ('[itemprop="legalName"]', '.company-name', '.companyName',
                     '#companyName', '[data-testid="company-name"]',
                     '[itemtype*="Organization"] > [itemprop="name"]',
                     '[itemtype*="LocalBusiness"] > [itemprop="name"]', 'h1'):
        for tag in soup.select(selector):
            value = clean(tag.get_text(" "))
            if valid_company_name(value):
                return value
    for node in organization_nodes(raw):
        value = clean(node.get("legalName") or node.get("name"))
        if valid_company_name(value) and "blue book" not in value.lower():
            return value
    for tag in raw.select('meta[property="og:title"], meta[name="twitter:title"], title'):
        value = clean(tag.get("content") or tag.get_text(" "))
        parts = re.split(r"\s+(?:[|–—]|-\s+(?=Locations|ProView|The Blue Book))\s*", value, flags=re.I)
        value = re.sub(r"\s*[-|–—]\s*(?:Locations.*|ProView.*|The Blue Book.*)$", "", parts[0], flags=re.I)
        if valid_company_name(value) and re.search(r"key contacts|locations|telephone|phone|address", soup.get_text(" "), re.I):
            return value
    return ""


def extract_listing_companies(markup, url):
    """Save only details actually visible in each result card, before visiting gated profiles."""
    if access_problem(markup):
        return []
    soup = content_soup(markup)
    found = {}
    for link in soup.select('a[href]'):
        root = profile_root(canonical(link.get("href", ""), url))
        if not root:
            continue
        label = clean(link.get_text(" "))
        if not valid_company_name(label):
            continue
        identifier = re.search(r"/iProView/(\d+)/", root, re.I).group(1)
        if identifier in found:
            continue
        card = link
        # Stop at the first ancestor that contains another company's link. This
        # prevents assigning a neighboring company's phone/address to this one.
        for parent in list(link.parents)[:8]:
            if parent.name in {"body", "html", "[document]"}:
                break
            roots = {profile_root(canonical(a.get("href", ""), url)) for a in parent.select('a[href]')}
            roots.discard("")
            if roots != {root} or len(parent.get_text(" ", strip=True)) > 3000:
                break
            card = parent
            if parent.name in {"article", "li"} or re.search(r"result|listing|company-card|proview-card", " ".join(parent.get("class", [])), re.I):
                break
        data = Company(identifier, label, root, url, method="listing_card",
                       evidence="Published listing details only; profile/contact page may still need access.")
        text = card.get_text("\n", strip=True)
        data.phones = phones(text)
        for a in card.select('a[href^="tel:"]'):
            data.phones.extend(p for p in phones(a["href"]) if p not in data.phones)
        data.emails = emails(text)
        location = re.search(r"([A-Za-z .'-]+),\s*([A-Z]{2})(?:\s+(\d{5}(?:-\d{4})?))?", text)
        if location:
            data.city, data.state, data.postal_code = [clean(v) for v in location.groups()]
        for a in card.select('a[href]'):
            target = canonical(a["href"], url)
            if target and not is_bluebook(target) and ("website" in a.get_text(" ").lower() or a.get("itemprop") == "url"):
                data.website = target
        if data.emails:
            data.email_sources = [url]
        found[identifier] = data
    return list(found.values())


def extract_company(markup, url):
    root = profile_root(url)
    if not root:
        return None
    raw = BeautifulSoup(markup, "html.parser")
    people = structured_people(raw)
    soup = content_soup(markup)
    if access_problem(markup):
        return None
    name = company_name(raw, soup)
    if not name:
        return None
    all_lines = lines_in(soup)
    if name in all_lines:
        all_lines = all_lines[all_lines.index(name):]
    key_index = next((i for i, x in enumerate(all_lines) if x.lower() == "key contacts"), len(all_lines))
    company_lines = all_lines[:key_index]
    data = Company(re.search(r"/iProView/(\d+)/", root, re.I).group(1), name, root, url)
    company_text = "\n".join(company_lines)
    data.phones = phones(company_text)
    data.emails = emails(company_text)
    data.contacts = parse_contacts(all_lines)
    for person in people:
        existing = next((c for c in data.contacts if c.name.casefold() == person.name.casefold()), None)
        if existing:
            existing.title = existing.title or person.title
            existing.phones.extend(p for p in person.phones if p not in existing.phones)
            existing.emails = sorted(set(existing.emails + person.emails))
        else:
            data.contacts.append(person)
    # US location, grounded in company content rather than the global city menu.
    location = re.search(r"([A-Za-z .'-]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)", company_text)
    if location:
        data.city, data.state, data.postal_code = map(clean, location.groups())
    address = soup.select_one('[itemprop="streetAddress"], address')
    if address:
        data.address = clean(address.get_text(" "))
    county = re.search(r"(?:County\s*:\s*)([A-Za-z .'-]+)", company_text, re.I)
    if county:
        data.county = clean(county.group(1))
    for a in soup.select("a[href]"):
        href = str(a.get("href", ""))
        label = clean(a.get_text(" ")).lower()
        if "website" in label or a.get("itemprop") == "url":
            target = canonical(href, url)
            host = urlsplit(target).hostname or ""
            if target and not is_bluebook(target) and not any(s in host for s in ("facebook.", "linkedin.", "twitter.", "instagram.", "dodge", "sweets.")):
                data.website = target
                break
    for node in organization_nodes(raw):
        node_name = clean(node.get("legalName") or node.get("name"))
        if node_name.casefold() != name.casefold():
            continue
        data.phones.extend(p for p in phones(str(node.get("telephone", ""))) if p not in data.phones)
        data.emails = sorted(set(data.emails + emails(str(node.get("email", "")))))
        addr = node.get("address")
        if isinstance(addr, dict):
            for field_name, schema_key in (("city", "addressLocality"), ("state", "addressRegion"), ("postal_code", "postalCode"), ("address", "streetAddress")):
                setattr(data, field_name, getattr(data, field_name) or clean(addr.get(schema_key)))
    for a in soup.select('a[href^="tel:"]'):
        # Contact-section phone links are already associated with their person.
        if key_index == len(all_lines):
            data.phones.extend(p for p in phones(a["href"]) if p not in data.phones)
    if data.emails:
        data.email_sources.append(url)
    return data


def discover(markup, url, broad=False):
    """Follow observed links; never manufacture page=2..N URLs."""
    soup = BeautifulSoup(markup, "html.parser")
    for tag in soup.select("script, style, noscript, footer, form, [role=dialog], .modal"):
        tag.decompose()
    found = {}
    current = urlsplit(canonical(url))
    current_query = dict(parse_qsl(current.query))
    for a in soup.select("a[href]"):
        target = canonical(a.get("href", ""), url)
        if not target or not is_bluebook(target):
            continue
        root = profile_root(target)
        if root:
            found[root] = "profile"
            continue
        path = urlsplit(target).path.lower()
        label = clean(a.get_text(" ")).lower()
        rel = a.get("rel", [])
        paging_context = a.find_parent(attrs={"class": re.compile(r"pag(?:e|in)|pager", re.I)})
        has_page_query = any(k.lower() in {"page", "p", "pg", "pageno", "pageindex", "start", "offset"} for k, _ in parse_qsl(urlsplit(target).query))
        same_results = path == current.path.lower() and all(
            dict(parse_qsl(urlsplit(target).query)).get(k) == v
            for k, v in current_query.items() if k.lower() not in {"page", "p", "pg", "pageno", "pageindex", "start", "offset"})
        if ("next" in rel or paging_context or (same_results and has_page_query)) and target != canonical(url):
            if label.isdigit() or re.search(r"next|last|[»›→]", label) or "next" in rel or has_page_query:
                found[target] = "listing"
        elif broad and (path in {"/search.html", "/search"} or "/cl/" in path or "/construction/" in path or "/directory/" in path or "/classifications/" in path or "/regions/" in path):
            if not any(x in path for x in ("login", "signup", "advertis")):
                found[target] = "listing"
    return sorted(found.items())

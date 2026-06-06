#!/usr/bin/env python3
# =============================================================================
# build.py — static site generator for J Star Technologies
#
# Pre-renders the design (originally a React/Babel prototype from Claude Design)
# into plain static HTML so the site deploys with no build step and no runtime
# framework. Content lives here; run `python3 build.py` to regenerate the pages.
#
#   Output: index.html, zero-to-ten.html, fractional-cto.html
#   Styling (jstar.css / site.css / home.css / pages.css), app.js, assets/ and
#   fonts/ are hand-maintained alongside this file.
# =============================================================================
import re

# ---- contact / brand constants ---------------------------------------------
EMAIL = "lets.code.net@gmail.com"
DEMO = "mailto:lets.code.net@gmail.com?subject=Book%20a%20demo"
ADVISORY_MAILTO = "mailto:lets.code.net@gmail.com?subject=Advisory%20consultation"
LOCATION = "Remote-first · North America"
EMAIL_UPPER = EMAIL.upper()

HOME, ZT, CTO = "index.html", "zero-to-ten.html", "fractional-cto.html"

# ---- escaping ---------------------------------------------------------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def att(s):
    return esc(s).replace('"', "&quot;")

# ---- thin-stroke line icons (Lucide-style, 1.8px) — from shared.jsx ---------
ICONS = {
    "spark":     '<path d="M12 3v5M12 16v5M3 12h5M16 12h5"/><path d="M6.5 6.5l3 3M14.5 14.5l3 3M17.5 6.5l-3 3M9.5 14.5l-3 3"/>',
    "shield":    '<path d="M12 3l7 3v5c0 4.6-3.1 7.9-7 9-3.9-1.1-7-4.4-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "trending":  '<path d="M3 17l5-5 3 3 7-7"/><path d="M16 8h4v4"/>',
    "wallet":    '<path d="M3 7.5A1.5 1.5 0 0 1 4.5 6H19a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4.5A1.5 1.5 0 0 1 3 17.5z"/><path d="M16 12.5h2"/>',
    "blueprint": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 9v11"/>',
    "cpu":       '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3"/>',
    "layers":    '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "search":    '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "rocket":    '<path d="M5 15c-1.5 1.5-2 5-2 5s3.5-.5 5-2"/><path d="M9 13c5-5 8-5 11-5 0 3 0 6-5 11l-3-1-2-2z"/><circle cx="14.5" cy="9.5" r="1.4"/>',
    "gauge":     '<path d="M12 14l4-4"/><path d="M5 18a8 8 0 1 1 14 0"/>',
    "lock":      '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "check":     '<path d="M5 12l4 4 10-10"/>',
    "flask":     '<path d="M9 3h6M10 3v6l-5 8a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-8V3"/>',
}

def icon(name, size=20):
    inner = ICONS.get(name, ICONS["spark"])
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">%s</svg>') % (size, size, inner)

# ---- site content (from data.jsx + page-local arrays) -----------------------
STATS = [
    ("20", "+", "Years in BizTech leadership"),
    ("11", "", "Countries running on our platforms"),
    ("99.9", "%", "Uptime across operated systems"),
    ("0", "", "Technical debt carried to scale"),
]

PERSONAS = [
    ("Funded Startups",
     "You need to ship fast without re-platforming in 12 months.",
     "We compress your MVP-to-production timeline with AI-accelerated execution, then harden the architecture so it survives your Series A traffic — not just the demo.",
     "MVP → PRODUCTION · NO REWRITE"),
    ("Enterprise Teams",
     "You need isolation, compliance, and architecture you can audit.",
     "Multi-tenant data isolation, RBAC and Row-Level Security at the database layer, idempotent FinTech integrations — designed to pass diligence and scale globally.",
     "SOC 2 PRACTICES · RLS · RBAC"),
    ("Private Equity",
     "You need an objective read on a stack before — and after — you buy.",
     "Technical due diligence, rescue operations, and fractional architecture leadership that stabilizes a buckling platform and lays a credible roadmap to scale.",
     "DUE DILIGENCE · RESCUE · ROADMAP"),
]

CAPABILITIES = [
    ("spark", "01", "AI-Driven Development", "CLAUDE · COPILOT · AZURE OPENAI",
     "We accelerate delivery with an AI-assisted engineering model, paired with Lovable + Supabase stacks for rapid MVP-to-production transitions.",
     ["AI-assisted core workflow", "Lovable + Supabase rapid stacks", "Document intelligence built in"]),
    ("shield", "02", "Multi-Tenant Systems & Security", "RLS · RBAC · SOC 2",
     "Rock-solid, isolated data architectures aligned with SOC 2 practices — security designed at the database layer, not bolted on.",
     ["Strict tenant data isolation", "Row-Level Security (RLS)", "Role-Based Access Control (RBAC)"]),
    ("trending", "03", "GTM & Technical SEO", "GROWTH ARCHITECTURE",
     "Architecture that drives growth — aligning system design with organic user acquisition and community research strategies.",
     ["SEO-engineered app structure", "Rendering & content pipelines", "Organic acquisition by design"]),
    ("wallet", "04", "Integration & Embedded FinTech", "IDEMPOTENT · WEBHOOK-SECURE",
     "Handling high-volume transactions with strict idempotency, retry mechanisms, and webhook security you can rely on.",
     ["High-volume transaction handling", "Idempotency & retry logic", "Validated webhook security"]),
]

VENTURES_OWNED = [
    ("xTen.pro", "J STAR VENTURE", "gold", "https://xten.pro",
     "A fully owned, internally developed SaaS platform: AI-driven growth audits, technical SEO, and management tooling engineered for the education and tutoring sector.",
     ["AI GROWTH AUDITS", "TECHNICAL SEO", "EDTECH"]),
    ("Zanbio.com", "CO-FOUNDED PLATFORM", "blue", "https://zanbio.com",
     "We developed the AI-driven accounts receivable & payable automation engine that helps finance teams eliminate manual workflows and accelerate cash collection.",
     ["AR / AP AUTOMATION", "AI FINANCE", "CO-FOUNDED"]),
]
VENTURES_CLIENT = [
    ("Qwiik.com", "CORE APP & INFRASTRUCTURE", "blue", "https://qwiik.com",
     "Scaled a multi-tenant SaaS platform from scratch to production — now operating across 11 countries and thousands of users, with AI document intelligence and embedded FinTech payments.",
     ["11 COUNTRIES", "EMBEDDED FINTECH", "AI DOC INTELLIGENCE"]),
]

STACK = [
    ("AI & LLMs", ["Claude", "Azure OpenAI", "GitHub Copilot", "Semantic Kernel"]),
    ("Frontend", ["Next.js", "React", "TypeScript", "Tailwind"]),
    ("Backend & Data", ["Supabase", "PostgreSQL", ".NET", "Node.js"]),
    ("Security", ["Row-Level Security", "RBAC", "SOC 2", "Auth / SSO"]),
    ("FinTech", ["Stripe", "Webhooks", "Idempotency", "Midtrans"]),
    ("DevOps", ["Azure", "Vercel", "Docker", "CI / CD"]),
]

LEADERS = [
    ("AS", "Ashish Sehajpal", "blue", "AI-Native Architect · Technology Leader",
     'Frames the technical vision. 20+ years in BizTech and a decade in LogTech, with a proven track record in "zero-to-ten" environments — taking ideas from concept to production rapidly, without accumulating technical debt.',
     ["ENTERPRISE ARCHITECTURE", "AI INTEGRATION", "TECHNICAL SEO"]),
    ("GS", "Geeta Sehajpal", "gold", "Co-Owner · Strategy & Operations",
     "Drives strategic direction and operational leadership — ensuring J Star delivers on its enterprise commitments with the rigor and reliability that scaling clients depend on.",
     ["STRATEGIC DIRECTION", "OPERATIONS", "DELIVERY"]),
]

PIPELINE = [
    ("01", 'THE "ZERO"', "Blueprint & Logic", "blueprint",
     "Before writing code, we map the business logic. Drawing on deep logistics and B2B workflow experience, we architect the database structures, security perimeters, and API integrations your growth model demands.",
     ["Data schema design", "Security perimeter", "API integration map"]),
    ("02", "THE BUILD", "AI-Accelerated Execution", "cpu",
     "We deploy our AI-assisted stack to rapidly generate the core application — connecting front-end interfaces to secure backend schemas at unprecedented speed.",
     ["AI-assisted generation", "Front-end to schema wiring", "Days, not months"]),
    ("03", 'THE "TEN"', "Validation & Hardening", "shield",
     "Where MVPs usually fail — and where J Star excels. We harden the infrastructure, validate data flows, optimize complex queries, and ready the platform for enterprise-grade usage.",
     ["Security review", "Query optimization", "Load readiness"]),
    ("04", "CONTINUOUS", "Continuous Scale", "rocket",
     "Your product launches on a foundation built to sustain massive growth — ready to integrate new features, users, and AI capabilities without missing a beat.",
     ["Feature-ready", "Multi-branch scale", "AI-capability ready"]),
]

ADVISORY = [
    ("01", "layers", "Enterprise System Architecture",
     "High-level architectural design for multi-tenant SaaS platforms — strict data isolation, scalable schemas, and enterprise-grade security (RBAC, RLS). We design the foundation so your in-house team executes with confidence."),
    ("02", "cpu", "AI Integration & Workflow Automation",
     "Transition your engineering teams to AI-assisted workflows (Claude, Copilot) and integrate AI capabilities — document intelligence, automated workflows — directly into your core product."),
    ("03", "search", "Technical SEO & Growth Architecture",
     "Align your technology stack with aggressive growth strategies — engineering application structure, rendering methods, and content pipelines to dominate search and drive organic acquisition."),
    ("04", "flask", "Tech Due Diligence & Rescue Operations",
     "Comprehensive technical audits assessing technical debt, security vulnerabilities, and team capability — followed by actionable roadmaps to stabilize and scale."),
]

ADVANTAGES = [  # zeroten.jsx
    ("rocket", "Rapid Prototyping", "We move from conceptual logic to functional interfaces in days, not months — eliminating the friction of boilerplate coding."),
    ("wallet", "Cost-Efficient Execution", "Your budget goes toward solving complex business problems, not paying for hours of manual syntax writing."),
    ("gauge", "Iterative Velocity", "Feedback loops are shortened, allowing us to pivot and adapt features in real time as you learn."),
]
HUMAN_ENG = [  # zeroten.jsx
    ("layers", "Multi-Tenant Architecture", "Strict data isolation, scalable database schemas, and seamless onboarding — designed in from the first table."),
    ("lock", "Enterprise Security", "Robust Role-Based Access Control (RBAC) and Row-Level Security (RLS) implemented right at the database layer."),
    ("wallet", "Transaction Integrity", "Highly reliable integration points handling FinTech workloads with strict idempotency and webhook validation."),
    ("shield", "System Validation", "Rigorous architecture and security reviews before a single line of code hits production."),
]
WHY = [  # cto.jsx
    ("01", "High-Impact Expertise", "Access tier-one architectural knowledge without the long-term commitment of a full-time executive salary."),
    ("02", "Unbiased Strategic Direction", "Get an external, objective perspective on your tech stack, team structure, and vendor choices."),
    ("03", "Accelerated Velocity", "Prevent costly architectural mistakes before a single line of code is written — drastically reducing time-to-market."),
]

# ---- shared chrome ----------------------------------------------------------
def brand():
    return ('<a class="brand" href="' + HOME + '">'
            '<img src="assets/jstar-mark.png" alt="J Star Technologies">'
            '<div class="wm">J STAR<em>Technologies</em></div></a>')

def nav(page):
    home = page == "home"
    def L(anchor):
        return anchor if home else HOME + anchor
    links = [
        ("Capabilities", L("#capabilities"), False),
        ("Ventures", L("#ventures"), False),
        ("Tech Stack", L("#stack"), False),
        ("Zero-to-Ten", ZT, page == "zeroten"),
        ("Advisory", CTO, page == "cto"),
    ]
    items = "".join(
        '<a href="%s"%s>%s</a>' % (href, ' class="active"' if active else "", label)
        for label, href, active in links
    )
    return ('<header class="nav"><div class="nav-in">' + brand() +
            '<nav class="nav-links">' + items + '</nav>'
            '<div class="nav-cta">'
            '<a class="btn btn-primary" href="' + DEMO + '">Book a demo <span class="arr">→</span></a>'
            '</div></div></header>')

def footer(page):
    home = page == "home"
    def L(anchor):
        return anchor if home else HOME + anchor
    return (
        '<footer class="footer"><div class="foot-grid">'
        '<div class="foot-brand">' + brand() +
        '<p>AI-Native engineering partner. We architect enterprise-grade, multi-tenant '
        'AI &amp; SaaS platforms — and operate our own. Backed by 20+ years of BizTech '
        'and a decade of LogTech.</p>'
        '<div class="foot-contact">'
        '<a href="mailto:' + EMAIL + '">' + EMAIL + '</a>'
        '<a href="#">' + LOCATION + '</a>'
        '</div></div>'
        '<div class="foot-col"><h6>Platform</h6><ul>'
        '<li><a href="' + L("#capabilities") + '">Capabilities</a></li>'
        '<li><a href="' + L("#stack") + '">Tech Stack</a></li>'
        '<li><a href="' + ZT + '">Zero-to-Ten</a></li>'
        '<li><a href="' + L("#ventures") + '">Ventures</a></li>'
        '</ul></div>'
        '<div class="foot-col"><h6>Services</h6><ul>'
        '<li><a href="' + CTO + '">Fractional CTO</a></li>'
        '<li><a href="' + CTO + '">Architecture Advisory</a></li>'
        '<li><a href="' + CTO + '">Tech Due Diligence</a></li>'
        '<li><a href="' + ZT + '">AI Integration</a></li>'
        '</ul></div>'
        '<div class="foot-col"><h6>Ventures</h6><ul>'
        '<li><a href="https://qwiik.com" target="_blank" rel="noopener">Qwiik ↗</a></li>'
        '<li><a href="https://zanbio.com" target="_blank" rel="noopener">Zanbio ↗</a></li>'
        '<li><a href="https://xten.pro" target="_blank" rel="noopener">xTen.pro ↗</a></li>'
        '</ul></div></div>'
        '<div class="foot-base">'
        '<span>© 2026 J STAR TECHNOLOGIES · ALL RIGHTS RESERVED</span>'
        '<span class="glyphs"><span>AI-NATIVE</span><span class="star-glyph">★</span>'
        '<span>MULTI-TENANT</span><span class="star-glyph">★</span>'
        '<span>SECURE BY DESIGN</span></span></div></footer>'
    )

def page(title, desc, css, page_id, body):
    sheets = "".join('<link rel="stylesheet" href="%s">' % c for c in css)
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="theme-color" content="#070A14">\n'
        '<title>' + esc(title) + '</title>\n'
        '<meta name="description" content="' + att(desc) + '">\n'
        '<link rel="icon" type="image/png" href="assets/jstar-mark.png">\n'
        + sheets + '\n</head>\n<body>\n'
        + nav(page_id) + '\n<main>\n' + body + '\n</main>\n'
        + footer(page_id) + '\n'
        '<script src="app.js" defer></script>\n'
        '</body>\n</html>\n'
    )

# ---- HOME sections ----------------------------------------------------------
def home_hero():
    return (
        '<section class="hero">'
        '<div class="glow-a"></div><div class="glow-b"></div><div class="grid-tex"></div>'
        '<div class="shell hero-in">'
        '<img class="hero-mark" src="assets/jstar-mark.png" alt="J Star Technologies">'
        '<div class="eyebrow" style="margin-bottom:22px">AI-NATIVE ENGINEERING PARTNER · BIZTECH × LOGTECH</div>'
        '<h1>Shipping production-grade AI &amp; <span class="grad-gold-text">SaaS architecture</span>.</h1>'
        '<p class="hero-lead">We turn rapid concepts into secure, scalable platforms. Backed by decades '
        'of BizTech and LogTech experience, J Star builds the multi-tenant infrastructure and AI '
        'capabilities that power enterprise growth.</p>'
        '<div class="hero-actions">'
        '<a class="btn btn-primary btn-lg" href="' + DEMO + '">Start your architecture <span class="arr">→</span></a>'
        '<a class="btn btn-ghost btn-lg" href="' + ZT + '">See the Zero-to-Ten method</a>'
        '</div>'
        '<div class="hero-fine">SOC 2 PRACTICES · MULTI-TENANT BY DEFAULT · ZERO TECHNICAL DEBT</div>'
        '</div></section>'
    )

def home_stats():
    cells = "".join(
        '<div class="stat"><div class="n">%s<span class="u">%s</span></div>'
        '<div class="l">%s</div></div>' % (esc(n), esc(u), esc(l))
        for n, u, l in STATS
    )
    return ('<section class="section tight band"><div class="shell">'
            '<div class="stats reveal">' + cells + '</div></div></section>')

def home_persona():
    btns = ""
    for i, (label, line, body, proof) in enumerate(PERSONAS):
        btns += (
            '<button class="persona-btn%s" data-line="%s" data-body="%s" data-proof="%s">'
            '<span class="idx">0%d</span>%s</button>' % (
                " on" if i == 0 else "", att(line), att(body), att(proof), i + 1, esc(label))
        )
    p0 = PERSONAS[0]
    panel = (
        '<div class="persona-fade">'
        '<div class="pline">' + esc(p0[1]) + '</div>'
        '<p class="pbody">' + esc(p0[2]) + '</p>'
        '<div class="pproof"><span class="star-glyph">★</span> ' + esc(p0[3]) + '</div>'
        '</div>'
    )
    return (
        '<section class="section"><div class="shell">'
        '<div class="sec-head reveal">'
        '<div class="marker"><span class="star-glyph">★</span> WHO WE WORK WITH</div>'
        '<h2>Built for the way you scale.</h2></div>'
        '<div class="persona reveal">'
        '<div class="persona-toggle">' + btns + '</div>'
        '<div class="persona-panel">' + panel + '</div>'
        '</div></div></section>'
    )

def home_capabilities():
    cards = ""
    for ic, n, title, tag, body, points in CAPABILITIES:
        pts = "".join('<li><span class="ck">%s</span>%s</li>' % (icon("check", 15), esc(p)) for p in points)
        cards += (
            '<div class="cap-card reveal">'
            '<div class="cap-top"><div class="cap-ic">' + icon(ic, 22) + '</div>'
            '<div class="cap-n">' + esc(n) + '</div></div>'
            '<h3>' + esc(title) + '</h3>'
            '<div class="cap-tag">' + esc(tag) + '</div>'
            '<p>' + esc(body) + '</p>'
            '<ul class="cap-points">' + pts + '</ul></div>'
        )
    return (
        '<section class="section band" id="capabilities"><div class="shell">'
        '<div class="sec-head reveal"><div class="marker"><b>§ 01</b> · THE PROWESS</div>'
        '<h2>Enterprise capability, not a list of services.</h2>'
        '<p class="lead">Four disciplines we architect together — translating deep technical skill '
        'into outcomes that move your business.</p></div>'
        '<div class="cap-grid">' + cards + '</div></div></section>'
    )

def venture_card(v, client):
    name, kind, accent, href, body, tags = v
    initials = re.sub(r"\..*$", "", name)[:2]
    cls = "vent-card" + (" client" if client else "") + (" gold-accent" if accent == "gold" else "")
    tagspans = "".join("<span>%s</span>" % esc(t) for t in tags)
    return (
        '<a class="' + cls + '" href="' + att(href) + '" target="_blank" rel="noopener">'
        '<div class="vent-thumb ' + accent + '">'
        '<div class="glow"></div><div class="dots"></div>'
        '<div class="chrome"><i></i><i></i><i></i></div>'
        '<div class="mono">' + esc(initials) + '</div></div>'
        '<div class="vent-body">'
        '<div class="vent-kind">' + esc(kind) + '</div>'
        '<h3>' + esc(name) + '</h3>'
        '<p>' + esc(body) + '</p>'
        '<div class="vent-tags">' + tagspans + '</div>'
        '<span class="vent-visit">Visit ' + esc(name) + ' ↗</span>'
        '</div></a>'
    )

def home_ventures():
    owned = "".join(venture_card(v, False) for v in VENTURES_OWNED)
    client = "".join(venture_card(v, True) for v in VENTURES_CLIENT)
    return (
        '<section class="section" id="ventures"><div class="shell">'
        '<div class="sec-head reveal"><div class="marker"><b>§ 02</b> · ECOSYSTEM &amp; SUCCESSES</div>'
        '<h2>We build for others — and operate our own IP.</h2>'
        '<p class="lead">A portfolio that proves the model: platforms we own and ventures we '
        'co-founded, beside production systems we architected for clients.</p></div>'
        '<div class="reveal"><div class="vent-label">Owned &amp; Co-Founded Ventures</div>'
        '<div class="vent-grid">' + owned + '</div></div>'
        '<div class="reveal" style="margin-top:32px"><div class="vent-label">Client Architecture</div>'
        '<div class="vent-grid single">' + client + '</div></div>'
        '</div></section>'
    )

def home_stack():
    chips = '<button class="fchip on">ALL</button>'
    for cat, _ in STACK:
        chips += '<button class="fchip" data-cat="%s">%s</button>' % (att(cat), esc(cat.upper()))
    tiles = ""
    for cat, items in STACK:
        for name in items:
            mono = re.sub(r"[^A-Za-z0-9]", "", name)[:2]
            tiles += (
                '<div class="tech" data-cat="' + att(cat) + '">'
                '<div class="tech-mark">' + esc(mono) + '</div>'
                '<div><div class="tech-name">' + esc(name) + '</div>'
                '<div class="tech-cat">' + esc(cat) + '</div></div></div>'
            )
    return (
        '<section class="section band" id="stack"><div class="shell">'
        '<div class="sec-head reveal"><div class="marker"><b>§ 03</b> · THE STACK</div>'
        '<h2>The technologies we master.</h2>'
        '<p class="lead">A modern, AI-native stack — battle-tested in production across our ventures '
        'and client systems. Filter by discipline.</p></div>'
        '<div class="stack-filters reveal">' + chips + '</div>'
        '<div class="stack-grid reveal">' + tiles + '</div>'
        '</div></section>'
    )

def home_zt_teaser():
    steps = "".join(
        '<div class="zt-step"><div class="zn">%s</div>'
        '<div class="zt-t">%s</div><div class="zs">%s</div></div>' % (esc(n), esc(title), esc(tier))
        for n, tier, title, _ic, _body, _meta in PIPELINE
    )
    return (
        '<section class="section"><div class="shell">'
        '<div class="zt-band reveal"><div class="grid-tex"></div>'
        '<div class="zt-left">'
        '<div class="marker"><span class="star-glyph">★</span> THE METHODOLOGY</div>'
        '<h2>The Zero-to-Ten framework.</h2>'
        '<p>Most agencies build a fragile "Zero-to-One" MVP that gets torn down at scale. We build '
        "for next year's enterprise traffic from day one — AI speed, architectural integrity.</p>"
        '<a class="btn btn-primary" href="' + ZT + '">See the full methodology <span class="arr">→</span></a>'
        '</div>'
        '<div class="zt-steps">' + steps + '</div>'
        '</div></div></section>'
    )

def home_leadership():
    cards = ""
    for initials, name, accent, role, body, tags in LEADERS:
        tagspans = "".join("<span>%s</span>" % esc(t) for t in tags)
        cls = "lead-card reveal" + (" gold-accent" if accent == "gold" else "")
        cards += (
            '<div class="' + cls + '">'
            '<div class="lead-av ' + accent + '"><span class="star star-glyph">★</span>' + esc(initials) + '</div>'
            '<div class="lead-info"><div class="lead-role">' + esc(role) + '</div>'
            '<h3>' + esc(name) + '</h3><p>' + esc(body) + '</p>'
            '<div class="lead-tags">' + tagspans + '</div></div></div>'
        )
    return (
        '<section class="section band" id="leadership"><div class="shell">'
        '<div class="sec-head reveal"><div class="marker"><b>§ 04</b> · LEADERSHIP</div>'
        '<h2>The people behind the architecture.</h2></div>'
        '<div class="lead-grid">' + cards + '</div></div></section>'
    )

def home_cta():
    return (
        '<section class="section" id="contact"><div class="shell">'
        '<div class="cta-band reveal"><div class="grid-tex"></div>'
        '<div class="cta-band-in">'
        '<div class="eyebrow" style="margin-bottom:18px">LET\'S ARCHITECT YOUR NEXT MOVE</div>'
        '<h2>Stop building prototypes. <span class="dim">Start building platforms.</span></h2>'
        "<p>Tell us where you're headed. We'll map the architecture, the AI leverage, and the path "
        'from concept to enterprise scale.</p>'
        '<div class="cta-actions">'
        '<a class="btn btn-gold btn-lg" href="' + DEMO + '">Book a demo <span class="arr">→</span></a>'
        '<a class="btn btn-ghost btn-lg" href="' + CTO + '">Explore advisory</a>'
        '</div>'
        '<div class="cta-fine">USUALLY A REPLY WITHIN ONE BUSINESS DAY · ' + EMAIL_UPPER + '</div>'
        '</div></div></div></section>'
    )

def build_home():
    body = "".join([
        home_hero(), home_stats(), home_persona(), home_capabilities(),
        home_ventures(), home_stack(), home_zt_teaser(), home_leadership(), home_cta(),
    ])
    return page(
        "J Star Technologies — AI-Native Engineering Partner",
        "J Star Technologies architects enterprise-grade, multi-tenant AI & SaaS platforms. "
        "Production-grade architecture, AI-accelerated, secure by design.",
        ["jstar.css", "site.css", "home.css"], "home", body,
    )

# ---- ZERO-TO-TEN sections ---------------------------------------------------
def zt_hero():
    return (
        '<section class="phero">'
        '<div class="glow-a"></div><div class="glow-b"></div><div class="grid-tex"></div>'
        '<div class="shell phero-in"><div class="phero-grid">'
        '<div><div class="eyebrow">THE ZERO-TO-TEN METHODOLOGY</div>'
        '<h1>Speed meets <span class="grad-blue-text">architectural integrity</span>.</h1>'
        '<p class="phero-lead">Most agencies build a "Zero-to-One" MVP — a fragile proof-of-concept '
        "torn down and rewritten when it's time to scale. We don't build for tomorrow's demo. We "
        "build for next year's enterprise traffic.</p>"
        '<div class="phero-actions">'
        '<a class="btn btn-primary btn-lg" href="' + DEMO + '">Architect your platform <span class="arr">→</span></a>'
        '<a class="btn btn-ghost btn-lg" href="#pipeline">See the pipeline</a></div>'
        '<div class="phero-fine">AI-ACCELERATED · ROCK-SOLID · MULTI-TENANT · SECURE FROM DAY ONE</div></div>'
        '<div class="reveal">'
        '<div class="compare-card good" style="margin-bottom:14px">'
        '<div class="compare-tag">★ ZERO-TO-TEN</div><h3>Built to carry the load.</h3>'
        '<p>AI compresses the timeline; decades of BizTech and LogTech experience keep the '
        'architecture rock-solid, multi-tenant, and secure.</p>'
        '<div class="verdict">' + icon("check", 15) + ' SCALES WITHOUT A REWRITE</div></div>'
        '<div class="compare-card bad"><div class="compare-tag">ZERO-TO-ONE</div>'
        '<h3 style="font-size:20px">Fragile by design.</h3>'
        '<p style="font-size:14px">A proof-of-concept that ultimately has to be torn down and '
        'rewritten the moment real traffic arrives.</p></div>'
        '</div></div></div></section>'
    )

def zt_ainative():
    cards = "".join(
        '<div class="adv-card reveal"><div class="adv-ic">%s</div>'
        '<h3>%s</h3><p>%s</p></div>' % (icon(ic, 21), esc(title), esc(body))
        for ic, title, body in ADVANTAGES
    )
    return (
        '<section class="section band"><div class="shell">'
        '<div class="sec-head reveal"><div class="marker"><b>§ 01</b> · THE AI-NATIVE ADVANTAGE</div>'
        '<h2>A force multiplier.</h2>'
        '<p class="lead">We operate an AI-assisted engineering model. By integrating tools like Claude '
        'and Copilot into our core workflow, we eliminate the friction of boilerplate — and spend our '
        'cycles where they matter.</p></div>'
        '<div class="adv-grid">' + cards + '</div></div></section>'
    )

def zt_human():
    rows = "".join(
        '<div class="point-row reveal"><div class="point-ic">%s</div>'
        '<div><h4>%s</h4><p>%s</p></div></div>' % (icon(ic, 20), esc(title), esc(body))
        for ic, title, body in HUMAN_ENG
    )
    return (
        '<section class="section"><div class="shell">'
        '<div class="sec-head reveal"><div class="marker"><b>§ 02</b> · HUMAN ENGINEERING WHERE IT COUNTS</div>'
        '<h2>AI writes the syntax. Humans design the systems.</h2>'
        '<p class="lead">By offloading repetitive coding to AI, our engineering focus shifts entirely '
        'to the "hard stuff" that makes or breaks a SaaS platform.</p></div>'
        '<div class="points-grid">' + rows + '</div></div></section>'
    )

def zt_pipeline():
    nodes = ""
    for i, (n, tier, title, ic, body, meta) in enumerate(PIPELINE):
        nodes += (
            '<div class="pipe-node%s" data-i="%d"><div class="pipe-dot"></div>'
            '<div class="pipe-n">%s</div><div class="pipe-label">%s</div></div>' % (
                " on" if i == 0 else "", i, esc(n), esc(title))
        )
    details = ""
    for i, (n, tier, title, ic, body, meta) in enumerate(PIPELINE):
        metaspans = "".join('<span><span class="d"></span>%s</span>' % esc(m) for m in meta)
        details += (
            '<div class="pipe-detail%s" data-i="%d"%s>'
            '<div class="pipe-detail-ic">%s</div>'
            '<div><div class="pipe-tier">%s</div><h3>%s</h3><p>%s</p></div>'
            '<div class="pipe-meta">%s</div></div>' % (
                " pipe-fade" if i == 0 else "", i,
                "" if i == 0 else ' style="display:none"',
                icon(ic, 30), esc(tier), esc(title), esc(body), metaspans)
        )
    return (
        '<section class="section band" id="pipeline"><div class="shell">'
        '<div class="sec-head reveal"><div class="marker"><b>§ 03</b> · THE ZERO-TO-TEN PIPELINE</div>'
        '<h2>From the "Zero" to the "Ten".</h2>'
        '<p class="lead">Four stages that turn business logic into an enterprise-ready platform. It '
        'advances on its own — or click any stage.</p></div>'
        '<div class="pipeline reveal"><div class="grid-tex"></div>'
        '<div class="pipe-rail"><div class="pipe-line"><i style="width:0%"></i></div>' + nodes + '</div>'
        + details +
        '<div class="pipe-controls"><button class="pipe-play">❚❚ Pause</button>'
        '<span class="pipe-stage" style="font-family:var(--font-mono);font-size:11px;color:var(--tx-3);letter-spacing:0.08em">STAGE 1 / 4</span>'
        '</div></div></div></section>'
    )

def zt_cta():
    return (
        '<section class="section"><div class="shell">'
        '<div class="cta-band reveal"><div class="grid-tex"></div><div class="cta-band-in">'
        '<div class="eyebrow" style="margin-bottom:18px">LET\'S ARCHITECT YOUR NEXT MOVE</div>'
        '<h2>Stop building prototypes. <span class="dim">Start building platforms.</span></h2>'
        '<p>Your product can launch on a foundation built to sustain massive growth — ready for new '
        'features, users, and AI capabilities without missing a beat.</p>'
        '<div class="cta-actions">'
        '<a class="btn btn-gold btn-lg" href="' + DEMO + '">Let\'s architect your next move <span class="arr">→</span></a>'
        '<a class="btn btn-ghost btn-lg" href="' + CTO + '">Fractional CTO &amp; advisory</a></div>'
        '<div class="cta-fine">' + EMAIL_UPPER + '</div>'
        '</div></div></div></section>'
    )

def build_zeroten():
    body = "".join([zt_hero(), zt_ainative(), zt_human(), zt_pipeline(), zt_cta()])
    return page(
        "The Zero-to-Ten Methodology — J Star Technologies",
        "Speed meets architectural integrity. J Star's Zero-to-Ten methodology compresses timelines "
        "with AI, while human engineering hardens the architecture for enterprise scale.",
        ["jstar.css", "site.css", "pages.css"], "zeroten", body,
    )

# ---- FRACTIONAL CTO sections ------------------------------------------------
def cto_hero():
    return (
        '<section class="phero">'
        '<div class="glow-a"></div><div class="grid-tex"></div>'
        '<div class="shell phero-in"><div class="phero-grid">'
        '<div><div class="eyebrow">FRACTIONAL CTO &amp; ARCHITECTURE ADVISORY</div>'
        '<h1>Strategic engineering leadership. <span class="grad-gold-text">Without the overhead</span>.</h1>'
        '<p class="phero-lead">Scaling an enterprise platform takes more than developers writing code '
        '— it takes a technical visionary who understands how architecture impacts the bottom line. '
        'Through J Star, Ashish Sehajpal provides Fractional CTO and Architecture Advisory for scaling '
        'startups, enterprise teams, and private equity firms.</p>'
        '<div class="phero-actions">'
        '<a class="btn btn-gold btn-lg" href="' + ADVISORY_MAILTO + '">Schedule a consultation <span class="arr">→</span></a>'
        '<a class="btn btn-ghost btn-lg" href="#engagements">View engagements</a></div>'
        '<div class="phero-fine">FRACTIONAL · ON-DEMAND · ENTERPRISE-GRADE</div></div>'
        '<div class="reveal"><div class="cto-portrait">'
        '<div class="glow"></div><div class="dots"></div>'
        '<div class="ph-note">PHOTO TO COME</div><div class="mono-av">AS</div>'
        '<div class="badge"><div class="nm">Ashish Sehajpal</div>'
        '<div class="rl">AI-Native Architect · Technology Leader</div></div>'
        '</div></div></div></div></section>'
    )

def cto_edge():
    return (
        '<section class="section band"><div class="shell">'
        '<div class="sec-head reveal" style="max-width:760px">'
        '<div class="marker"><b>§ 01</b> · THE EXECUTIVE EDGE</div>'
        '<h2>Engineering meets growth.</h2></div>'
        '<div class="edge reveal"><div>'
        '<p>Most CTOs focus purely on the code. Ashish brings a rare, holistic approach to technology '
        'leadership. With <strong>20+ years in BizTech</strong> and a decade operating in complex '
        '<strong>LogTech</strong> environments, he bridges the gap between system architecture and '
        'market expansion.</p>'
        "<p>As an AI-Native Architect, Growth Marketer, and Technical SEO Strategist, he doesn't just "
        'build systems to function — he architects systems to acquire users, handle high-volume B2B '
        'workflows, and scale globally.</p>'
        '<div class="edge-roles"><span>AI-Native Architect</span><span>Growth Marketer</span>'
        '<span>Technical SEO Strategist</span><span>Zero-to-Ten Operator</span></div></div>'
        '<div class="stats" style="grid-template-columns:1fr 1fr">'
        '<div class="stat"><div class="n">20<span class="u">+</span></div><div class="l">Years in BizTech leadership</div></div>'
        '<div class="stat"><div class="n">10<span class="u">+</span></div><div class="l">Years in complex LogTech</div></div>'
        '<div class="stat"><div class="n">11</div><div class="l">Countries on operated platforms</div></div>'
        '<div class="stat"><div class="n">0</div><div class="l">Technical debt to scale</div></div>'
        '</div></div></div></section>'
    )

def cto_engagements():
    cards = "".join(
        '<div class="eng-card reveal"><div class="eng-top">'
        '<div class="eng-ic">%s</div><div class="eng-n">%s</div></div>'
        '<h3>%s</h3><p>%s</p></div>' % (icon(ic, 22), esc(n), esc(title), esc(body))
        for n, ic, title, body in ADVISORY
    )
    return (
        '<section class="section" id="engagements"><div class="shell">'
        '<div class="sec-head reveal"><div class="marker"><b>§ 02</b> · CORE ADVISORY ENGAGEMENTS</div>'
        '<h2>Where architectural direction pays off.</h2>'
        '<p class="lead">Companies often need architectural direction as much as they need code. These '
        'are the engagements where a fractional leader moves the needle fastest.</p></div>'
        '<div class="eng-grid">' + cards + '</div></div></section>'
    )

def cto_why():
    cards = "".join(
        '<div class="why-card reveal"><div class="wn">%s</div><h4>%s</h4><p>%s</p></div>' % (
            esc(n), esc(title), esc(body))
        for n, title, body in WHY
    )
    return (
        '<section class="section band"><div class="shell">'
        '<div class="sec-head reveal"><div class="marker"><span class="star-glyph">★</span> WHY A FRACTIONAL CTO</div>'
        '<h2>Tier-one leadership, exactly when you need it.</h2></div>'
        '<div class="why-grid">' + cards + '</div></div></section>'
    )

def cto_cta():
    return (
        '<section class="section"><div class="shell">'
        '<div class="cta-band reveal"><div class="grid-tex"></div><div class="cta-band-in">'
        '<div class="eyebrow" style="margin-bottom:18px">ADVISORY</div>'
        '<h2>Secure the architecture of <span class="dim">your next phase.</span></h2>'
        '<p>Evaluating an acquisition, scaling past your MVP, or stabilizing a platform under strain? '
        'Start with a conversation.</p>'
        '<div class="cta-actions">'
        '<a class="btn btn-gold btn-lg" href="' + ADVISORY_MAILTO + '">Schedule an advisory consultation <span class="arr">→</span></a>'
        '<a class="btn btn-ghost btn-lg" href="' + ZT + '">See how we build</a></div>'
        '<div class="cta-fine">DIRECT WITH ASHISH · ' + EMAIL_UPPER + '</div>'
        '</div></div></div></section>'
    )

def build_cto():
    body = "".join([cto_hero(), cto_edge(), cto_engagements(), cto_why(), cto_cta()])
    return page(
        "Fractional CTO & Architecture Advisory — J Star Technologies",
        "Strategic engineering leadership without the overhead. Fractional CTO and Architecture "
        "Advisory for scaling startups, enterprise teams, and private equity firms.",
        ["jstar.css", "site.css", "pages.css"], "cto", body,
    )

# ---- write ------------------------------------------------------------------
if __name__ == "__main__":
    pages = {HOME: build_home(), ZT: build_zeroten(), CTO: build_cto()}
    for fname, html in pages.items():
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote %s (%d bytes)" % (fname, len(html.encode("utf-8"))))

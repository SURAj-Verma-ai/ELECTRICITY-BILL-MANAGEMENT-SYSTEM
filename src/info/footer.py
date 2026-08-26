"""Footer link content.

Each link is {"label", "endpoint"}. When `endpoint` is set it's a real
Flask endpoint name and the template resolves it with url_for. When it's
None, the link renders as an inert placeholder (see `placeholder-link` in
base.css), front-end only, nothing wired up yet. Swap `endpoint` in as
each page ships.
"""

LINK_GROUPS = [
    {
        "title": "Product",
        "links": [
            {"label": "Features", "endpoint": "features"},
            {"label": "Pricing", "endpoint": None},
            {"label": "Integrations", "endpoint": None},
            {"label": "Changelog", "endpoint": None},
        ],
    },
    {
        "title": "Company",
        "links": [
            {"label": "About", "endpoint": "about"},
            {"label": "Careers", "endpoint": None},
            {"label": "Press", "endpoint": None},
            {"label": "Contact", "endpoint": None},
        ],
    },
    {
        "title": "Legal",
        "links": [
            {"label": "Privacy Policy", "endpoint": None},
            {"label": "Terms of Service", "endpoint": None},
            {"label": "Cookie Policy", "endpoint": None},
            {"label": "Refund Policy", "endpoint": None},
            {"label": "Security Policy", "endpoint": None},
            {"label": "Accessibility Statement", "endpoint": None},
            {"label": "All Policies", "endpoint": None},
        ],
    },
]

BOTTOM_LINKS = ["Status", "Documentation", "Contact"]

# shown as cards above the footer, all placeholder for now
IMPORTANT_LINKS = [
    {"icon": "\U0001F4C4", "label": "Billing Guide"},
    {"icon": "\U0001F4CA", "label": "Tariff Info"},
    {"icon": "\U0001F4DE", "label": "Support Center"},
    {"icon": "\U0001F4DD", "label": "Grievance Cell"},
    {"icon": "\U0001F310", "label": "Open Data"},
    {"icon": "\U0001F4E6", "label": "Consumer Portal"},
]

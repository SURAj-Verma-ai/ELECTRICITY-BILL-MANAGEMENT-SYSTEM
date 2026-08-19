"""Static content for the home, features, and about pages, kept separate
from routing/templates so copy can change without touching either."""

HERO = {
    "badge": "Track. Manage. Stay ahead.",
    "subtitle": "Track usage, keep every bill in one place, and stay on top of your account, "
    "all from a single dashboard.",
}

# Short strip shown on the home page, linking out to the full /features page.
HIGHLIGHTS = [
    {"icon": "⚡", "title": "Usage Tracking"},
    {"icon": "🧾", "title": "Bill Management"},
    {"icon": "📊", "title": "Usage Insights"},
    {"icon": "🔒", "title": "Secure Access"},
]

FEATURES_INTRO = "Everything you need to stay on top of your electricity bills, in one place."

FEATURES = [
    {
        "icon": "⚡",
        "title": "Usage Tracking",
        "description": "Monitor your electricity consumption in real time and spot trends before the bill arrives.",
    },
    {
        "icon": "🧾",
        "title": "Bill Management",
        "description": "View, organize, and download every bill in one place, no more digging through paperwork.",
    },
    {
        "icon": "📊",
        "title": "Usage Insights",
        "description": "Clear breakdowns and reports that make it easy to understand where your usage is going.",
    },
    {
        "icon": "🔒",
        "title": "Secure Access",
        "description": "Your account is protected with hashed passwords and strict credential requirements.",
    },
]

ABOUT_INTRO = "A small, focused tool for a problem that shouldn't need a spreadsheet."

ABOUT = {
    "heading": "Built to make electricity billing simple",
    "paragraphs": [
        "EBMS gives you one place to track usage, review bills, and stay ahead of due dates, "
        "instead of digging through paper statements or scattered PDFs.",
        "It's built to be fast, secure, and straightforward, with nothing to configure before "
        "you get real value out of it.",
    ],
    "points": [
        "Works for households and small businesses",
        "Your data stays in your account, never sold or shared",
        "No spreadsheets or manual tracking required",
    ],
}

# Sample feedback used to preview the layout, not real submissions yet.
REVIEWS = [
    {
        "quote": "Finally a clean way to see all my bills without hunting through email.",
        "author": "A. Sharma",
        "role": "Homeowner",
    },
    {
        "quote": "Setup took two minutes and I already know where my usage spikes are.",
        "author": "R. Fernandes",
        "role": "Small business owner",
    },
    {
        "quote": "Simple, fast, and it just works, exactly what I wanted.",
        "author": "M. Chen",
        "role": "Early user",
    },
]

import os
import datetime
from flask import Flask, render_template, request
from dotenv import load_dotenv
from peewee import *
from playhouse.shortcuts import model_to_dict

load_dotenv()
app = Flask(__name__)

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase("file:memory?mode=memory&cache=shared", uri=True)
else:
    mydb = MySQLDatabase(
        os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306,
    )
print(mydb)


class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = mydb


mydb.connect()
mydb.create_tables([TimelinePost])

education = [
    {
        "school": "CEGEP - John Abbott College",
        "degree": "DEC in Science",
        "location": "St-Anne-de-Bellevue, Quebec",
        "years": "2021 – 2023",
    },
    {
        "school": "Concordia University",
        "degree": "Bachelor of Engineering, Software Engineering",
        "location": "Montreal, Quebec",
        "years": "2023 – 2028",
    },
]

# "logo" is a filename in static/img/logos; roles without one fall back to a
# monogram drawn from the company name.
work_experience = [
    {
        "title": "Infrastructure Engineer - Shopify",
        "tag": "Incoming",
        "years": "Sept 2026 – Dec 2026",
        "description": "Joining the Data Streaming Infrastructure team.",
        "logo": "logo-shopify.png",
        "url": "https://www.shopify.com",
    },
    {
        "title": "Production Engineering Fellow - Meta × MLH Fellowship",
        "tag": "Fellowship",
        "years": "Jun 2026 – Sept 2026",
        "description": "Production engineering track of the MLH Fellowship, sponsored by Meta.",
        "logo": "logo-meta.png",
        "url": "https://fellowship.mlh.io",
    },
    {
        "title": "Software Engineer Intern - Bombardier Aerospace (Engineering Systems)",
        "tag": "Internship",
        "years": "Jan 2026 – Aug 2026",
        "description": "Maintained an internal document release system used by Bombardier Champions and Suppliers.",
        "logo": "logo-bombardier.png",
        "url": "https://www.bombardier.com",
    },
    {
        "title": "Part-Time Sushi Chef",
        "tag": "Earlier",
        "description": "Prepared sushi and managed service at a small sushi spot.",
    },
]

# Displayed as tags on the home page. These are the technologies this site
# itself is built and deployed with — add to the list as that changes.
skills = [
    "Python",
    "Flask",
    "MySQL",
    "Docker",
    "NGINX",
    "GitHub Actions",
    "Linux",
    "JavaScript",
    "HTML & CSS",
]

# The three headline projects, each shown large with a pair of screenshots.
# Image filenames live in static/img/projects.
featured_projects = [
    {
        "name": "mtl minted",
        "tag": "Winner · McHacks",
        "description": (
            "A platform for artists to mint and tokenize their identity on "
            "Solana, with on-chain ownership handled by custom Anchor programs."
        ),
        "stack": ["Solana", "Rust", "Anchor", "React"],
        "images": ["original.png", "original2.png"],
        "links": [
            {"label": "Code on GitHub", "url": "https://github.com/zaifnatra/solana"},
            {"label": "Devpost", "url": "https://devpost.com/software/black-beauty"},
        ],
    },
    {
        "name": "shorten.it",
        "tag": "3rd overall · Meta × MLH",
        "description": (
            "A URL shortener built to survive production, load tests, injected "
            "outages, and a live Grafana view of it all holding together."
        ),
        "stack": ["Flask", "Redis", "PostgreSQL", "Grafana"],
        "images": ["screenShot.png", "dashboard.png"],
        "links": [
            {"label": "Code on GitHub", "url": "https://github.com/zaifnatra/MetaHackathon"},
            {"label": "Devpost", "url": "https://devpost.com/software/shorten-it"},
        ],
    },
    {
        "name": "retro secrets",
        "tag": "Winner · ConUHacks",
        "description": (
            "Messages hidden in plain sight, steganography with custom "
            "encryption, wrapped in a small social platform for passing them around."
        ),
        "stack": ["Python", "TypeScript"],
        "images": ["retro1.png", "retro.png"],
        "links": [
            {"label": "Code on GitHub", "url": "https://github.com/deltag0/ConUHacks"},
            {"label": "Devpost", "url": "https://devpost.com/software/retro-secrets"},
        ],
    },
]

# Everything else, shown in a smaller grid below the featured three.
other_projects = [
    {
        "name": "gear pack",
        "description": "Track and share hiking and mountaineering gear across a group of friends.",
        "stack": ["Next.js", "TypeScript", "Supabase", "Prisma"],
        "image": "S1.jpg",
        "links": [
            {"label": "GitHub", "url": "https://github.com/zaifnatra/gear-pack"},
            {"label": "Live", "url": "https://gear-pack.vercel.app/"},
        ],
    },
    {
        "name": "ev prediction model",
        "description": "Predicting electric vehicle specs from a trained scikit-learn model, deployed on Streamlit.",
        "stack": ["Python", "scikit-learn", "Streamlit"],
        "image": "ev.png",
        "links": [
            {"label": "GitHub", "url": "https://github.com/zaifnatra/ev-ml"},
            {"label": "Live", "url": "https://ev-prediction-zaifnatra.streamlit.app/"},
        ],
    },
    {
        "name": "heroes journey",
        "description": "A 2D puzzle adventure through a randomized maze, written from scratch in Java.",
        "stack": ["Java"],
        "image": "heroes1.jpg",
        "links": [
            {"label": "GitHub", "url": "https://github.com/zaifnatra/spaceus"},
        ],
    },
    {
        "name": "campus events",
        "description": "Ticketing platform for students to discover, organize and attend events on campus.",
        "stack": ["JavaScript", "MongoDB"],
        "image": "campus.jpg",
        "links": [
            {"label": "GitHub", "url": "https://github.com/zaifnatra/SOEN341-F25"},
            {"label": "Live", "url": "https://soen341-f25.onrender.com/"},
        ],
    },
]

project_count = len(featured_projects) + len(other_projects)

socials = [
    {"label": "GitHub", "url": "https://github.com/zaifnatra"},
    {"label": "LinkedIn", "url": "https://linkedin.com/in/huzaifa-fareed"},
]

# Scrolling band under the hero. "Title - Company" gets flipped so the
# company reads first, which is what the eye catches at that size.
marquee_items = []
for _job in work_experience:
    if " - " in _job["title"]:
        _role, _company = _job["title"].split(" - ", 1)
        marquee_items.append(f"{_company} · {_role}")
    else:
        marquee_items.append(_job["title"])

# Hackathon placements ride along in the same band.
marquee_items += [p["tag"] for p in featured_projects if p.get("tag")]

# Character cap the timeline form enforces in the browser. The API itself
# accepts any non-empty content; this only shapes the front end.
MAX_CONTENT_LENGTH = 500

hobbies = [
    {
        "image": "hobby1.jpg",
        "alt": "Fishing",
        "caption": "Fishing! Most common fish I caught is catfish",
    },
    {
        "image": "hobby2.JPG",
        "alt": "Hiking",
        "caption": "Hiking! This is my friend and I trekking in Peru",
    },
]


@app.context_processor
def inject_nav():
    links = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if rule.endpoint == "static" or "GET" not in rule.methods:
            continue
        # API routes return JSON, not pages — keep them out of the nav.
        if rule.rule.startswith("/api"):
            continue
        label = (
            "Home"
            if rule.rule == "/"
            else rule.rule.strip("/").replace("_", " ").title()
        )
        links.append({"label": label, "url": rule.rule})
    return {"nav_links": links}


@app.route("/")
def index():
    return render_template(
        "index.html",
        title="Huzaifa Fareed",
        tagline="Software Engineering @ Concordia | MLH Production Engineering Fellow",
        url=os.getenv("URL"),
        education=education,
        work_experience=work_experience,
        skills=skills,
        featured_projects=featured_projects,
        other_projects=other_projects,
        project_count=project_count,
        socials=socials,
        marquee_items=marquee_items,
    )


@app.route("/hobbies")
def hobbies_page():
    return render_template(
        "hobbies.html",
        title="Hobbies",
        url=os.getenv("URL"),
        hobbies=hobbies,
    )


@app.route("/timeline")
def timeline():
    return render_template(
        "timeline.html",
        title="Timeline",
        url=os.getenv("URL"),
        max_content_length=MAX_CONTENT_LENGTH,
    )


@app.route("/api/timeline_post", methods=["POST"])
def post_time_line_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    content = request.form.get("content", "").strip()

    if not name:
        return "Invalid name", 400
    if not content:
        return "Invalid content", 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return "Invalid email", 400

    timeline_post = TimelinePost.create(name=name, email=email, content=content)

    return model_to_dict(timeline_post)


@app.route("/api/timeline_post", methods=["GET"])
def get_time_line_post():
    return {
        "timeline_posts": [
            model_to_dict(p)
            for p in TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }


@app.route("/api/timeline_post/<int:post_id>", methods=["DELETE"])
def delete_time_line_post(post_id):
    deleted = TimelinePost.delete_by_id(post_id)
    if deleted == 0:
        return {"error": f"No timeline post with id {post_id}"}, 404
    return {"deleted": post_id}

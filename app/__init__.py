import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

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

work_experience = [
    {
        "title": "Software Engineer Intern - Shopify",
        "tag": "Incoming",
        "description": "Incoming Software Engineer Intern (details TBD).",
    },
    {
        "title": "Software Engineer Intern - Bombardier Aerospace (Engineering Systems)",
        "tag": "Internship",
        "description": "Maintained an internal document release system used by Bombardier Champions and Suppliers.",
    },
    {
        "title": "Part-Time Sushi Chef",
        "tag": "Earlier",
        "description": "Prepared sushi and managed service at a small sushi spot.",
    },
]

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
        title="MLH Fellow",
        url=os.getenv("URL"),
        education=education,
        work_experience=work_experience,
    )


@app.route("/hobbies")
def hobbies_page():
    return render_template(
        "hobbies.html",
        title="Hobbies",
        url=os.getenv("URL"),
        hobbies=hobbies,
    )

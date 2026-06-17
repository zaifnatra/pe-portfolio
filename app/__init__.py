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
        "title": "Part-Time Sushi Chef",
        "tag": "Earlier",
        "description": "Worked as a sushi chef at a small sushi spot.",
    },
    {
        "title": "Aviation Cybersecurity Intern - Bombardier Aerospace",
        "tag": "Internship",
        "description": "Learning about attack protocols and security vulnerabilities in aviation systems.",
    },
    {
        "title": "Engineering Systems Intern - Bombardier Aerospace",
        "tag": "Internship",
        "description": "Maintained an internal document release system used by Bombardier Champions and Suppliers, ensuring accurate and timely distribution of engineering documentation.",
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
        label = "Home" if rule.rule == "/" else rule.rule.strip("/").replace("_", " ").title()
        links.append({"label": label, "url": rule.rule})
    return {"nav_links": links}


@app.route('/')
def index():
    return render_template(
        'index.html',
        title="MLH Fellow",
        url=os.getenv("URL"),
        education=education,
        work_experience=work_experience,
    )


@app.route('/hobbies')
def hobbies_page():
    return render_template(
        'hobbies.html',
        title="Hobbies",
        url=os.getenv("URL"),
        hobbies=hobbies,
    )

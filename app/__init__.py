import os
import datetime
from flask import Flask, render_template, request
from dotenv import load_dotenv
from peewee import *
from playhouse.shortcuts import model_to_dict

load_dotenv()
app = Flask(__name__)

mydb = MySQLDatabase(
    os.getenv("MYSQL_DB"),
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


@app.route("/api/timeline_post", methods=["POST"])
def post_time_line_post():
    name = request.form["name"]
    email = request.form["email"]
    content = request.form["content"]
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

# Production Engineering - Week 1 - Portfolio Site

Welcome to the MLH Fellowship! During Week 1, you'll be using Flask to build a portfolio site. This site will be the foundation for activities we do in future weeks so spend time this week making it your own and reflect your personality!

## Tasks

Once you've got your portfolio downloaded and running using the instructions below, you should attempt to complete the following tasks.

For each of these tasks, you should create an [Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) and work on them in a new [branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches). When the task has been completed, you should open a [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) and get another fellow in your pod to give you feedback before merging it in.

_Note: Make sure to include a link to the Issue you're progressing on inside of your Pull Request so your reviewer knows what you're progressing on!_

### GitHub Tasks

- [x] Create Issues for each task below
- [x] Progress on each task in a new branch
- [x] Open a Pull Request when a task is finished to get feedback

### Portfolio Tasks

- [x] Add a photo of yourself to the website
- [x] Add an "About youself" section to the website.
- [x] Add your previous work experiences
- [x] Add your hobbies (including images)
- [x] Add your current/previous education
- [x] Add a map of all the cool locations/countries you visited

### Flask Tasks

- [x] Get your Flask app running locally on your machine using the instructions below.
- [x] Add a template for adding multiple work experiences/education/hobbies using [Jinja](https://jinja.palletsprojects.com/en/3.0.x/api/#basics)
- [x] Create a new page to display hobbies.
- [x] Add a menu bar that dynamically displays other pages in the app

## Repository Layout

| Path | Purpose |
| --- | --- |
| `app/` | Flask application (routes, templates, static assets). |
| `tests/` | Unit tests for the app and the database model. |
| `user_conf.d/` | Nginx site config mounted into the `nginx` container. |
| `Dockerfile` | Image definition for the Flask app. |
| `docker-compose.yml` | Local development stack (Flask + MariaDB, port 5000 published). |
| `docker-compose.prod.yml` | Production stack on the VPS (Flask + MariaDB + nginx/certbot on 80/443). |
| `example.env` | Template for `.env`, listing every environment variable the app uses. |
| `redeploy-site.sh` | Pulls `origin/main` on the VPS and rebuilds the production containers. |
| `run_test.sh` | Runs the full unit test suite against the project virtualenv. |
| `requirements.txt` | Python dependencies. |
| `.gitignore` | Keeps the virtualenv, `.env`, and caches out of the repo. |

The following files are additions beyond the standard fellowship template.

- `.dockerignore` - keeps the virtualenv, `.git`, and caches out of the Docker build context so image builds stay small and fast.
- `.gitattributes` - forces LF line endings on the shell scripts.
  Without it, Git on Windows checks them out with CRLF and the containers fail with `bad interpreter: /bin/bash^M`.
- `curl-test.sh` - end-to-end API check (POST, GET, DELETE against `/api/timeline_post`) written for the Week 5 exercise.
- `.github/` - issue templates, a pull request template, and a contributing guide used for the Week 1 GitHub workflow tasks.
- `docs/deployment-notes.md` - VPS runbook: SSH details, redeploy steps, firewall and certbot gotchas.

## Getting Started

### 2026-06-16

- Updated requirements.txt to ensure all the dependancies work with Python 3.14 in order to run the project locally
- Created 9 GitHub issues for the tasks assigned for this week
- Tested to run the project locally on my machine, used WSL to run the project.

### 2026-06-17

- Completed all tasks required
- 3 PRs, first one for static html content, second one for refactoring of static content with Jinja template, lastly third one for implementing dynamic nav bar with a seperate hobbies page

### 2026-06-19

- All 3 PR's merged.

## Installation

Make sure you have python3 and pip installed

Create and activate virtual environment using virtualenv

```bash
$ python -m venv python3-virtualenv
$ source python3-virtualenv/bin/activate
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all dependencies!

```bash
pip install -r requirements.txt
```

## Usage

Create a .env file using the example.env template (make a copy using the variables inside of the template)

Start flask development server

```bash
$ export FLASK_ENV=development
$ flask run
```

You should get a response like this in the terminal:

```
❯ flask run
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

You'll now be able to access the website at `localhost:5000` or `127.0.0.1:5000` in the browser!

_Note: The portfolio site will only work on your local machine while you have it running inside of your terminal. We'll go through how to host it in the cloud in the next few weeks!_

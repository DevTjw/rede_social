<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/badge/Python-3.11_|_3.12_|_3.14-blue" />
  <img src="https://img.shields.io/badge/Django-4+-0C4B33" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
  <img src="https://img.shields.io/badge/WebSockets-Django%20Channels-orange" />
  ====================================================================
</p>

📘 Internal Social Network

An internal social networking platform with feeds, follower system, real-time private messaging (WebSockets), and customizable user profiles.
Designed for companies, teams, and communities requiring fast, organized, centralized communication.
====================================================================
📂 Features
🔐 Authentication & Profiles

User registration, login, and logout

Integrated Django Authentication

Custom user profiles

Permission control (user, client, administrator)

====================================================================
📰 Feed & Posts

Create posts with text, images, or attachments

Likes and comments

Feed based on followed users

Explore section to discover new profiles

====================================================================
🤝 Followers System

Follow / unfollow users

Feed generated dynamically from followed profiles

Optional internal notifications

====================================================================
💬 Real-Time Messaging

One-to-one user chat

Optional: only connected users or mutual followers

WebSockets using Django Channels

Message history stored in the database

Online / offline presence indicator (optional)

====================================================================
🧩 API & Front-end

Well-structured Django views

Responsive templates with Bootstrap 5

Clean and consistent routing

Optional REST API using Django REST Framework

====================================================================
🛠 Tech Stack
Component	Details
Framework	Django 4+
Language	Python 3.11 – 3.14
Database	SQLite (dev) / PostgreSQL (prod)
WebSockets	Django Channels
Broker	Redis
Async Tasks (optional)	Celery
Front-end	HTML, CSS, Bootstrap 5

====================================================================
📦 Installation
1. Clone the repository
git clone https://github.com/devtjw/rede-social.git
cd rede-social-interna

2. Install dependencies
pip install -r requirements.txt

3. Apply migrations
python manage.py migrate

4. Run the server
python manage.py runserver

5. Start WebSockets (if using Channels)
daphne project.asgi:application

====================================================================
📅 Roadmap

 Notifications system

 Internal groups / communities

 Group chat

 Dark mode

 Video upload

 Full REST API (DRF)

 Automated tests

====================================================================
🧑‍💻 Contributing

Pull requests are welcome.
For major changes, please open an issue to discuss them first.

====================================================================
📜 License

MIT License.


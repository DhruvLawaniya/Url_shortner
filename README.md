🔗 Shortify | URL Shortener <br>
![alt text](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)

![alt text](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi)

![alt text](https://img.shields.io/badge/PostgreSQL-Cloud-336791?style=for-the-badge&logo=postgresql)

![alt text](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?style=for-the-badge&logo=tailwind-css)

A high-performance, URL shortening service built to demonstrate modern backend architecture, cloud database integration, and real-time analytics.
[The links produced currently are not as short as expected since I didn't deem it necessary to pay for a domain. This project is educational and should be treated as such.]

🌐 Live Demo Link (https://url-shortner-vma9.onrender.com/?short_url=PW3EPi)

🚀 Features
Instant Redirection: Optimized backend logic for sub-100ms URL redirection.

Click Analytics: Real-time tracking of link engagement with a persistent click counter.

URL Deduplication: Intelligent database checks to prevent duplicate entries for the same target URL.

PRG Pattern Implementation: Utilizes the Post-Redirect-Get design pattern to prevent "form resubmission" errors upon page refresh.

Responsive Dashboard: A clean, mobile-friendly UI built with Tailwind CSS and Jinja2 Templates.

Privacy-First Notice: Integrated user disclaimer regarding the public nature of shortened links.

🛠️ Tech Stack
Layer	Technology
Backend	Python 3.12, FastAPI
Database	PostgreSQL (Neon), SQLAlchemy ORM
Frontend	Jinja2, Tailwind CSS, HTML5
Deployment	Render (CI/CD via GitHub)
Dev Tools	Uvicorn, Pip, Virtualenv
📸 Screenshots



🧠 Key Technical Challenges Solved

1. The "Double-Submit" Problem
Implemented the Post-Redirect-Get (PRG) pattern. By returning a 303 Redirect after a successful POST request, I ensured that users refreshing the page would not accidentally re-trigger the URL creation logic.

2. Database Resilience in the Cloud
Configured the application to dynamically switch between SQLite (for local development) and PostgreSQL (for production) using environment variables. I also implemented SSL requirement handling specifically for cloud database providers like Neon.tech.

3. Data Integrity
Added a deduplication layer that checks the database for existing long URLs before generating a new short code, saving storage space and maintaining cleaner analytics.

📄 License
Distributed under the MIT License. See LICENSE for more information.

Contact
Dhruv Lawaniya - https://www.linkedin.com/in/dhruvlawaniya/
Project Link: https://github.com/dhruvlawaniya/url-shortener



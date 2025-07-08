# 🗳️ Vo & Pet School — School Voting Platform

![Project Banner](https://raw.githubusercontent.com/Mykhailo-Tr/IT-Turik2/main/banner.png)

---

## 🎓 Introduction

This project is a **web platform for organizing democratic voting within a school environment**.

The system facilitates seamless interaction between students, parents, teachers, and school administration to make collective decisions through voting and petitions.  
It supports flexible voting levels (class, group), deadlines, initiator roles, and a threshold-based petition mechanism.

---

## 🔍 Core Objectives

### 🚀 Extra Features
- Light/Dark theme toggle

- WebSocket notifications for new petitions/votes

- Petition read confirmation by teachers/director

- Mobile-first responsive UI

- Modular structure for easy extensibility

### ✅ The platform allows:
- Creation of class/group votes and petitions
- Real-time vote counting via **WebSockets**
- Event synchronization with an interactive calendar (**FullCalendar**)
- Role-based access for students, teachers, and parents, director
- Commenting and supporting petitions
- User profile management and activity tracking
- Petition approval workflow by director (50%+1 support threshold)

---

## 🛠️ Technologies Used

| Technology | Description |
|-----------|-------------|
| ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) **Python 3.10+** | Core programming language |
| ![Django](https://img.shields.io/badge/-Django-092E20?logo=django&logoColor=white&style=flat-square) **Django 5.2** | Web framework (models, views, URLs, ORM) |
| ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?logo=postgresql&logoColor=white&style=flat-square) **PostgreSQL** | Relational database |
| ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white&style=flat-square) **Docker + Compose** | Containerization & deployment |
| ![WebSocket](https://img.shields.io/badge/-WebSockets-35495E?logo=socket.io&logoColor=white&style=flat-square) **Django Channels** | Real-time communication (votes, petitions, notifications) |
| ![FullCalendar](https://img.shields.io/badge/-FullCalendar-F69C00?logo=javascript&logoColor=white&style=flat-square) **FullCalendar.js** | Interactive event calendar |
| ![Bootstrap](https://img.shields.io/badge/-Bootstrap-7952B3?logo=bootstrap&logoColor=white&style=flat-square) **Bootstrap 5** | Styling & responsive UI |
| ![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?logo=javascript&logoColor=black&style=flat-square) **JavaScript (ES6)** | Dynamic UI, AJAX logic |
| ![AOS](https://img.shields.io/badge/-AOS.js-000000?logo=aos&logoColor=white&style=flat-square) **AOS.js** | UI animations |
| ![Pytest](https://img.shields.io/badge/-Pytest-0A9EDC?logo=pytest&logoColor=white&style=flat-square) **Pytest + Coverage** | Testing and code quality |

---

## 🧠 Architecture Overview

- `accounts/` — custom user model and roles (Student, Parent, Teacher)
- `voting/` — voting logic, options, results
- `petitions/` — petitions, support logic, approval
- `calendarapp/` — AJAX-based calendar integration
- `notifications/` — real-time alerts via WebSockets
- `activity/` — user history and participation tracking
- `schoolgroups/` — class and teacher group organization

---

## 💡 Design Patterns & Practices

| Pattern | Usage |
|--------|-------|
| **Decorator** | `@login_required`, role restrictions |
| **Mixin** | Reusable logic in CBVs |
| **Factory** | `get_or_create` for statuses and events |
| **Command** | Status change or petition approval commands |
| **Observer** | WebSocket-based event broadcasting |
| **DRY & CBVs** | Clean, reusable Django architecture |

---

## ⚙️ Project Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mykhailo-Tr/IT-Turik2.git
   cd IT-Turik2
   ```

### 🐧 Option 1: Linux/macOS Setup
2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

### 🪟 Option 2: Windows Setup
2. **Run the setup script**
   ```bash
   setup.bat
   ```

### 🔁 Option 3: Manual Docker Setup


2. **Build and run Docker containers**
   ```bash
   docker-compose up --build
   ```

3. **Initialize the database**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py collectstatic --noinput
   docker-compose exec web python manage.py compilemessages
   ```

4. **Create superuser (optional)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Run tests (optional)**
   ```bash
   docker-compose exec web pytest
   ```

## 👥 Team & Roles

| Contributor        | Role & Contribution                                                                 |
|--------------------|--------------------------------------------------------------------------------------|
| **Mykhailo Tretiak** ([@Mykhailo-Tr](https://github.com/Mykhailo-Tr)) | Backend architecture, Django setup, WebSockets integration, Docker and Database setup, Frontend design and JS logic (AJAX), Testing       |
| **Denys Balyuk** ([@Mox1toGH](https://github.com/Mox1toGH))       | Frontend styling, modal integration, testing and polishing UX, Backend refactoring, Test integration, Testing                         |


---
## 🎉 Final Thoughts

We hope you find this project useful and enjoyable! If you have any questions or feedback, don't hesitate to reach out to us at [rohatyn.team@gmail.com](mailto:rohatyn.team@gmail.com).

Best regards, the Rohatyn Team.

Happy coding! 🎓
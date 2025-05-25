# 🎉 Event Management API

A Django REST API for creating, managing, and registering for events such as conferences, workshops, or meetups.  
Includes features like user authentication, event registration, filtering, search, email notifications, and Docker
deployment.

🔗 [View on GitHub](https://github.com/vkleshko/Event-Management-API)

---

## 🚀 Features

- Event CRUD (Create, Read, Update, Delete)
- User authentication (JWT/Token)
- Registration for events
- Search and filtering
- Email notification on event registration
- API documentation via Swagger
- Dockerized setup for easy deployment

---

## ⚙️ Environment Variables (`.env`)

Create a `.env` file in the root directory:

```env
# Django
SECRET_KEY=django-insecure-your-secret-key
```

You can create your django key there [Djecrety](https://djecrety.ir)

```
# Email
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

How to create a Gmail App Password:

- Log in to your Google Account: https://myaccount.google.com/security
- Enable Two-Factor Authentication (2FA) if you haven’t done so already
- Go to the App Passwords section
- Select Other (Custom name) as the device type and enter a name like "Django Email"
- Click Generate and copy the 16-character password
- Use this password as your EMAIL_HOST_PASSWORD in the .env file

```
# PostgreSQL
POSTGRES_USER=event-management
POSTGRES_PASSWORD=event-management
POSTGRES_DB=event-management
POSTGRES_HOST=db
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data
```

---

## 🐳 Running with Docker

Clone the repository and navigate into the project:

```bash
git clone https://github.com/vkleshko/Event-Management-API.git
cd Event-Management-API
docker-compose up -d
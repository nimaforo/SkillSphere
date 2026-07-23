# SkillSphere - پروژه‌ های اشتراکی

![Django](https://img.shields.io/badge/Django-5.2-green)
![React](https://img.shields.io/badge/React-18-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

**A modern web platform for sharing and collaborating on projects with real-time chat, comments, and notifications.**

---

## 🎯 Features

### 👤 User Management
- ✅ **Email/Password Authentication** - Secure login and registration
- ✅ **Persistent Sessions** - Auto-login for 24 hours
- ✅ **User Profiles** - Edit bio, location, website
- ✅ **User Statistics** - Projects uploaded, likes received, comments, engagement score

### 📁 Projects
- ✅ **Upload Projects** - Support for PDF, ZIP, images
- ✅ **Project Feed** - Browse all shared projects
- ✅ **Comments** - Comment on projects with real-time updates
- ✅ **Likes** - Like/unlike projects instantly
- ✅ **Download** - Secure file downloads with authentication

### 💬 Communication
- ✅ **Real-time Chat** - WebSocket-based chat for project discussions
- ✅ **Live Notifications** - Get notified about likes, comments, and chat messages
- ✅ **Activity Tracking** - Track uploads, likes, and comments

### 📊 Analytics
- ✅ **User Dashboard** - View personal statistics and achievements
- ✅ **Engagement Metrics** - Track your project performance
- ✅ **Popular Projects** - See trending projects
- ✅ **Active Users** - Leaderboard of most active users

---

## 🛠️ Tech Stack

### Backend
- **Django 5.2** - Web framework
- **Django REST Framework** - API
- **PostgreSQL** - Database
- **Redis** - Cache & Message broker
- **Celery** - Background tasks
- **Channels** - WebSocket support
- **Docker** - Containerization

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide Icons** - Icons
- **WebSocket** - Real-time communication

### DevOps
- **Docker Compose** - Multi-container orchestration
- **Docker** - Containerization

---

## 📦 Installation

### Prerequisites
- Docker & Docker Compose
- Git
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Quick Start

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/skillsphere.git
cd skillsphere
```

#### 2. Create environment file
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=skillsphere
DB_USER=skillsphere_user
DB_PASSWORD=skillsphere_password
```

#### 3. Start Docker containers
```bash
docker-compose up -d
```

#### 4. Create a test user
```bash
docker-compose exec django python create_test_data.py
```

Credentials:
- Email: `test@example.com`
- Password: `testpass123`

#### 5. Start frontend development server
```bash
cd my-frontend
npm install
npm run dev
```

Access the application:
- **Frontend:** http://localhost:5174
- **Backend API:** http://127.0.0.1:8000
- **Django Admin:** http://127.0.0.1:8000/admin

---

## 🚀 Usage

### For Users

#### Registration & Login
1. Visit http://localhost:5174
2. Click "ثبت نام و عضویت" (Register)
3. Enter email and password
4. Your account is automatically saved and persistent

#### Upload a Project
1. Go to "مدیریت پروژه" (Project Management)
2. Click "آپلود پروژه" (Upload Project)
3. Select file (PDF, ZIP, JPG, PNG)
4. Add title and description
5. Click "آپلود کن" (Upload)

#### Interact with Projects
1. Go to "پروژه‌های مشترک" (Project Feed)
2. Like projects with ❤️
3. Add comments 💬
4. Download files 📥

#### Use Chat
1. Go to "چت" (Chat)
2. Join a project chat room
3. Send real-time messages

#### View Profile
1. Click "پروفایل کاربر" (Profile)
2. See your statistics and recent projects
3. Edit your bio, location, website
4. View your achievements and badges

---

## 📁 Project Structure

```
skillsphere/
├── backend/
│   ├── core/                 # Django settings
│   ├── users/               # User management
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── projects/            # Project management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── consumers.py     # WebSocket handlers
│   │   └── urls.py
│   ├── chat/                # Chat system
│   │   ├── consumers.py
│   │   └── routing.py
│   ├── manage.py
│   └── requirements.txt
│
├── my-frontend/             # React app
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Django container
└── README.md
```

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/register/           # Register new user
POST   /api/login/              # Login
POST   /api/token/refresh/      # Refresh JWT token
```

### Users
```
GET    /api/users/profile/      # Get user profile with stats
PUT    /api/users/profile/      # Update user profile
```

### Projects
```
GET    /api/projects/feed/      # List all projects
POST   /api/projects/upload/    # Upload new project
POST   /api/projects/feed/<id>/like/        # Like project
POST   /api/projects/feed/<id>/comment/     # Comment on project
GET    /api/projects/feed/<id>/download/   # Download project file
```

### Notifications
```
GET    /api/projects/notifications/                  # List notifications
POST   /api/projects/notifications/<id>/read/        # Mark as read
POST   /api/projects/notifications/<id>/delete/      # Delete notification
```

### WebSocket
```
ws://localhost:8000/ws/chat/1/?token=YOUR_JWT_TOKEN           # Chat
ws://localhost:8000/ws/notifications/?token=YOUR_JWT_TOKEN    # Notifications
```

---

## 🐳 Docker Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services (Keep Data)
```bash
docker-compose stop
```

### Restart Services
```bash
docker-compose restart
```

### View Logs
```bash
docker-compose logs -f django
docker-compose logs -f postgres
```

### Run Django Commands
```bash
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
```

### Delete Everything (Careful!)
```bash
docker-compose down -v
```

---

## 📊 Database Schema

### Users
```
- id: Integer (Primary Key)
- email: String (Unique)
- username: String
- first_name: String
- password: Hashed
- date_joined: DateTime
```

### Projects
```
- id: Integer (Primary Key)
- user: ForeignKey → User
- title: String
- description: Text
- file: File
- created_at: DateTime
- likes: ManyToMany → User
```

### Comments
```
- id: Integer (Primary Key)
- project: ForeignKey → Project
- user: ForeignKey → User
- content: Text
- created_at: DateTime
```

### Notifications
```
- id: Integer (Primary Key)
- recipient: ForeignKey → User
- sender: ForeignKey → User (Nullable)
- message: Text
- notification_type: String (like/chat/system)
- is_read: Boolean
- created_at: DateTime
```

### Activity Log
```
- id: Integer (Primary Key)
- user: ForeignKey → User
- activity_type: String (project_upload/project_like/project_comment)
- project: ForeignKey → Project
- description: Text
- created_at: DateTime
```

---

## 🔐 Data Persistence

Your data is automatically saved in Docker volumes:
- `postgres_data` - Database
- `redis_data` - Cache
- `elasticsearch_data` - Search data

**Important:** Use `docker-compose stop` or `docker-compose down` (NOT `docker-compose down -v`)

Read [DATA_PERSISTENCE_GUIDE.md](DATA_PERSISTENCE_GUIDE.md) for more details.

---

## 🧪 Testing

### Create Test Data
```bash
python create_test_data.py
```

### Access Django Admin
1. Create superuser:
   ```bash
   docker-compose exec django python manage.py createsuperuser
   ```
2. Visit http://127.0.0.1:8000/admin
3. Login with your credentials

---

## 📝 Environment Variables

Create a `.env` file:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=skillsphere
DB_USER=skillsphere_user
DB_PASSWORD=skillsphere_password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Frontend
FRONTEND_URL=http://localhost:5174
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose logs postgres

# Recreate database
docker-compose down
docker-compose up -d
```

### WebSocket Connection Failed
```bash
# Check if Channels is running
docker-compose logs django | grep "channels"

# Restart Django
docker-compose restart django
```

### Frontend Not Loading
```bash
# Install dependencies
cd my-frontend
npm install

# Clear cache
npm cache clean --force

# Restart dev server
npm run dev
```

---

## 📚 Documentation

- [DATA_PERSISTENCE_GUIDE.md](DATA_PERSISTENCE_GUIDE.md) - How data is saved
- [ACTIVITY_TRACKING_UPDATED.md](ACTIVITY_TRACKING_UPDATED.md) - Activity system
- [FIXES_COMPLETED.md](FIXES_COMPLETED.md) - Recent changes

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

Created with ❤️ for the developer community

---

## 📞 Support

For issues and questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review existing issues on GitHub
3. Create a new issue with detailed information

---

## 🎉 Features Roadmap

- [ ] Advanced search with filters
- [ ] User following system
- [ ] Project categories and tags
- [ ] Direct messaging between users
- [ ] Mobile app (React Native)
- [ ] Email notifications
- [ ] Project collaboration (multiple owners)
- [ ] API rate limiting
- [ ] User dashboard customization

---

**Built with ❤️ using Django, React, and Docker**

For the latest updates, visit: https://github.com/yourusername/skillsphere

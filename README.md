"# CodeForge - AI-Powered Adaptive Learning Platform

## Project Overview

CodeForge is an intelligent, AI-driven adaptive learning platform designed to help developers master coding skills through personalized problem-solving experiences. The platform leverages cutting-edge language models and adaptive AI mentorship to provide real-time guidance, code evaluation, and personalized learning roadmaps.

---

## Features

### Core Features
- **AI Mentor System**: Personalized guidance using multi-turn conversations with language models
- **Adaptive Learning Paths**: Dynamically generated roadmaps based on user progress
- **Diverse Problem Sets**: 45+ problems across multiple topics with varying difficulty levels
- **Real-time Code Evaluation**: Instant feedback on submitted solutions
- **Progress Tracking**: Monitor your learning journey with detailed statistics
- **Topic-based Learning**: Structured learning organized by data structures and algorithms

### Technical Features
- **Multi-topic Support**: Arrays, HashMaps, Sliding Window, Two Pointers, Stack, Queue, Linked Lists, Trees, Graphs, and more
- **Comprehensive Test Cases**: Visible and hidden test cases for rigorous evaluation
- **Authentication System**: Secure user authentication with JWT tokens
- **MongoDB Atlas Integration**: Scalable cloud database
- **Responsive UI**: Modern, intuitive interface built with React and Streamlit

---

## Tech Stack

### Backend
- **Framework**: FastAPI 0.115.0
- **Runtime**: Python 3.13
- **Database**: MongoDB Atlas (Async Motor driver)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **AI Integration**: Groq API with Langraph
- **Server**: Uvicorn

### Frontend
- **Framework**: React + TypeScript / Streamlit
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **HTTP Client**: Requests/Axios

---

## Architecture

```
CodeForge/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # MongoDB connection
│   ├── routes/                 # API endpoints
│   ├── services/               # Business logic
│   ├── agents/                 # AI Mentor agents
│   ├── schemas/                # Pydantic models
│   ├── seed/                   # Database seeding
│   └── requirements.txt
│
├── frontend/
│   ├── app.py                  # Streamlit main
│   ├── pages/                  # Multi-page app
│   └── package.json
│
├── README.md
├── .gitignore
├── .env.example
└── requirements.txt
```

---

## Installation

### Prerequisites
- Python 3.13+
- Node.js 18+
- MongoDB Atlas account
- Groq API key (optional, for AI mentor)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/CodeForge.git
cd CodeForge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Seed Database (Optional)

```bash
cd backend/seed
python seed.py
```

---

## Environment Variables

Create `.env` file:

```
PORT=8000
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/CodeForge?retryWrites=true&w=majority
DATABASE_NAME=CodeForge
JWT_SECRET=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GROQ_API_KEY=your-groq-key (optional)
LLM_MODEL=mixtral-8x7b-32768 (optional)
```

---

## Running Backend

```bash
cd backend
uvicorn main:app --reload
```

**API Documentation**: http://localhost:8000/docs

---

## Running Frontend

```bash
cd frontend
streamlit run app.py
```

**Frontend**: http://localhost:8501

---

## AI Mentor Workflow

The AI mentor uses a state-machine architecture with Langraph:

1. **Input Processing**: Parse user query and context
2. **Route Selection**: Determine appropriate response type
3. **Solution Generation**: Generate code solutions when needed
4. **Explanation**: Provide detailed explanations
5. **Hint Generation**: Offer progressive hints
6. **Feedback**: Constructive feedback on submissions

---

## Future Improvements

- Advanced analytics dashboards
- Real-time collaboration features
- Mobile application
- Multilingual support
- Video tutorials integration
- Community forum
- Gamification (badges, leaderboards)
- IDE integration
- Performance profiling

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

Bhuvan Nayak

---

## Support

For issues and questions, please open an issue on GitHub." 

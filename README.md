# Tech-Duolingo

Tech Duolingo is a gamified learning platform that helps users learn technical concepts through short lessons, quizzes, and interactive exercises. It focuses on making technology learning simple, engaging, and accessible.

## Features

- **Gamified Learning**: Earn points and track progress through interactive lessons
- **Tech Vocabulary**: Learn technical terms with definitions, examples, and code snippets
- **User Authentication**: Sign up and sign in to track your learning progress
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Feedback**: Immediate feedback on quiz answers

## Tech Stack

### Backend
- **FastAPI**: High-performance web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **SQLite**: Lightweight database for development
- **Passlib**: Password hashing and verification
- **Pydantic**: Data validation and serialization

### Frontend
- **React**: JavaScript library for building user interfaces
- **Vite**: Fast build tool and development server
- **ESLint**: Code linting and formatting

## Project Structure

```
Tech-Duolingo/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── requirements.txt # Python dependencies
│   └── __pycache__/     # Python cache files
├── frontend/
│   ├── public/          # Static assets
│   ├── src/             # React source code
│   │   ├── App.jsx      # Main React component
│   │   ├── main.jsx     # React entry point
│   │   └── assets/      # React assets
│   ├── package.json     # Node.js dependencies
│   ├── vite.config.js   # Vite configuration
│   └── eslint.config.js # ESLint configuration
└── README.md            # Project documentation
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Usage

1. Start both backend and frontend servers as described above
2. Open your browser and navigate to the frontend URL
3. Sign up for a new account or sign in with existing credentials
4. Start learning technical concepts through interactive lessons
5. Take quizzes to test your knowledge and earn points

## API Documentation

When the backend is running, visit `http://localhost:8000/docs` to view the interactive API documentation powered by Swagger UI.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

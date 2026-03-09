import React, { useState, useEffect } from "react";

const API_BASE = "http://localhost:8080";

function App() {
  const [view, setView] = useState("auth"); // auth | learn | game | dashboard
  const [authToken, setAuthToken] = useState(null); // token = user_id as string
  const [currentUser, setCurrentUser] = useState(null);
  const [sessionQuestions, setSessionQuestions] = useState(0);


  const [signUpData, setSignUpData] = useState({
    name: "",
    email: "",
    password: "",
  });
  const [signInData, setSignInData] = useState({
    email: "",
    password: "",
  });
  const [authMode, setAuthMode] = useState("signin"); // signin | signup
  const [authError, setAuthError] = useState("");

  const [terms, setTerms] = useState([]);
  const [termsError, setTermsError] = useState("");
  const [selectedTerm, setSelectedTerm] = useState(null);

  const [question, setQuestion] = useState(null);
  const [selectedOptionId, setSelectedOptionId] = useState(null);
  const [answerResult, setAnswerResult] = useState(null);
  const [showHint, setShowHint] = useState(false);

  const [stats, setStats] = useState(null);

  // add auth header helper
  const authHeaders = () => {
    if (!authToken) return {};
    return {
      "Content-Type": "application/json",
      "X-User-Id": authToken,
    };
  };

  const handleSignUp = async () => {
    setAuthError("");
    try {
      const res = await fetch(`${API_BASE}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(signUpData),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Sign up failed");
      }
      const user = await res.json();
      // after sign up, go to sign in view
      setAuthMode("signin");
      setSignInData({ email: signUpData.email, password: signUpData.password });
    } catch (e) {
      setAuthError(e.message);
    }
  };

  const handleSignIn = async () => {
    setAuthError("");
    try {
      const res = await fetch(`${API_BASE}/auth/signin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(signInData),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Sign in failed");
      }
      const data = await res.json();
      setAuthToken(data.token);
      setCurrentUser(data.user);
      setView("learn");
      // load terms initially
      fetchTerms(data.token);
    } catch (e) {
      setAuthError(e.message);
    }
  };

  const fetchTerms = async (tokenParam) => {
    const token = tokenParam || authToken;
    if (!token) return;
    setTermsError("");
    try {
      const res = await fetch(`${API_BASE}/terms`, {
        headers: {
          "Content-Type": "application/json",
          "X-User-Id": token,
        },
      });
      if (!res.ok) {
        let message = `Failed to load topics (${res.status})`;
        try {
          const err = await res.json();
          if (err?.detail) message = err.detail;
        } catch {}
        throw new Error(message);
      }
      const data = await res.json();
      setTerms(data);
    } catch (e) {
      setTerms([]);
      setTermsError(e.message || "Failed to load topics");
    }
  };

const startGame = async () => {
  if (!authToken) return;
  const res = await fetch(`${API_BASE}/game/question`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ mode: "definition" }),
  });
  if (!res.ok) return;
  const data = await res.json();
  setQuestion(data);
  setSelectedOptionId(null);
  setAnswerResult(null);
  setShowHint(false);
  setSessionQuestions(prev => prev + 1);  // 👈 NEW
  setView("game");
};


const submitAnswer = async () => {
  if (!authToken || !question || !selectedOptionId) return;
  const res = await fetch(`${API_BASE}/game/answer`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      term_id: question.term_id,
      selected_term_id: selectedOptionId,
    }),
  });
  if (!res.ok) return;
  const data = await res.json();
  setAnswerResult(data);
  fetchStats();
  
  if (sessionQuestions < 5) {
    setTimeout(() => startGame(), 5000);
  } else {
    setTimeout(() => {
      setSessionQuestions(0);  // 👈 RESET
      alert("🎉 Session complete! Check your dashboard.");
      setView("dashboard");
    }, 5000);
  }
};



  const fetchStats = async () => {
    if (!authToken) return;
    const res = await fetch(`${API_BASE}/users/me/stats`, {
      headers: authHeaders(),
    });
    if (!res.ok) return;
    const data = await res.json();
    setStats(data);
  };

  const logout = () => {
    setAuthToken(null);
    setCurrentUser(null);
      setView("auth");
      setTerms([]);
      setTermsError("");
      setSelectedTerm(null);
    setQuestion(null);
    setAnswerResult(null);
    setStats(null);
  };

  useEffect(() => {
    if (authToken) {
      fetchTerms();
    }
  }, [authToken]);

  // --------------- RENDER ---------------
  if (!authToken) {
    return (
      <div className="app">
        <header className="header">
          <h1>Tech Vocabulary Builder</h1>
        </header>
        <div className="auth-container">
          <div className="auth-toggle">
            <button
              className={authMode === "signin" ? "active" : ""}
              onClick={() => setAuthMode("signin")}
            >
              Sign In
            </button>
            <button
              className={authMode === "signup" ? "active" : ""}
              onClick={() => setAuthMode("signup")}
            >
              Sign Up
            </button>
          </div>

          {authMode === "signup" ? (
            <div className="auth-form">
              <h2>Create Account</h2>
              <input
                type="text"
                placeholder="Name"
                value={signUpData.name}
                onChange={(e) =>
                  setSignUpData({ ...signUpData, name: e.target.value })
                }
              />
              <input
                type="email"
                placeholder="Email"
                value={signUpData.email}
                onChange={(e) =>
                  setSignUpData({ ...signUpData, email: e.target.value })
                }
              />
              <input
                type="password"
                placeholder="Password"
                value={signUpData.password}
                onChange={(e) =>
                  setSignUpData({ ...signUpData, password: e.target.value })
                }
              />
              <button onClick={handleSignUp}>Sign Up</button>
              {authError && <p className="error">{authError}</p>}
            </div>
          ) : (
            <div className="auth-form">
              <h2>Sign In</h2>
              <input
                type="email"
                placeholder="Email"
                value={signInData.email}
                onChange={(e) =>
                  setSignInData({ ...signInData, email: e.target.value })
                }
              />
              <input
                type="password"
                placeholder="Password"
                value={signInData.password}
                onChange={(e) =>
                  setSignInData({ ...signInData, password: e.target.value })
                }
              />
              <button onClick={handleSignIn}>Sign In</button>
              {authError && <p className="error">{authError}</p>}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Authenticated view
  return (
    <div className="app">
      <header className="header">
        <h1>Tech Vocabulary Builder</h1>
        <div className="user-section">
          {currentUser && <span>Welcome, {currentUser.name}</span>}
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <nav className="nav">
        <button onClick={() => setView("learn")}>Learn Topics</button>
        <button onClick={startGame}>Play Game</button>
        <button
          onClick={() => {
            fetchStats();
            setView("dashboard");
          }}
        >
          Dashboard
        </button>
      </nav>

      <main className="main">
        {view === "learn" && (
          <LearnView
            terms={terms}
            termsError={termsError}
            selectedTerm={selectedTerm}
            setSelectedTerm={setSelectedTerm}
          />
        )}

        {view === "game" && (
          <GameView
            question={question}
            selectedOptionId={selectedOptionId}
            setSelectedOptionId={setSelectedOptionId}
            answerResult={answerResult}
            startGame={startGame}
            submitAnswer={submitAnswer}
            showHint={showHint}
            setShowHint={setShowHint}
          />
        )}

        {view === "dashboard" && <DashboardView stats={stats} />}
      </main>
    </div>
  );
}

function LearnView({ terms, termsError, selectedTerm, setSelectedTerm }) {
  return (
    <div className="learn">
      <div className="terms-list">
        <h2>Topics</h2>
        {termsError && <p className="error">{termsError}</p>}
        {!termsError && terms.length === 0 && <p>No topics found.</p>}
        {terms.map((t) => (
          <div
            key={t.id}
            className={
              "term-card " +
              (selectedTerm && selectedTerm.id === t.id ? "active" : "")
            }
            onClick={() => setSelectedTerm(t)}
          >
            <h3>{t.term}</h3>
            <p>{t.short_definition}</p>
            <span className="pill">{t.difficulty}</span>
          </div>
        ))}
      </div>
      <div className="term-detail">
        {selectedTerm ? (
          <>
            <h2>{selectedTerm.term}</h2>
            <p>
              <strong>Definition:</strong> {selectedTerm.detailed_explanation}
            </p>
            <p>
              <strong>Real world:</strong> {selectedTerm.real_world_example}
            </p>
            <div>
              <strong>Code snippet:</strong>
              <pre>{selectedTerm.example_code_snippet}</pre>
            </div>
          </>
        ) : (
          <p>Select a topic to read details.</p>
        )}
      </div>
    </div>
  );
}

function GameView({
  question,
  selectedOptionId,
  setSelectedOptionId,
  answerResult,
  startGame,
  submitAnswer,
  showHint,
  setShowHint,
}) {
  if (!question) {
    return (
      <div>
        <p>Click "Play Game" to get your first question.</p>
      </div>
    );
  }

  return (
    <div className="game">
      <h2>Guess the Term</h2>
      <p className="clue-label">Clue ({question.clue_type}):</p>
      <p className="clue-text">{question.clue_text}</p>

      <button className="hint-btn" onClick={() => setShowHint((prev) => !prev)}>
        {showHint ? "Hide Hint" : "Show Hint"}
      </button>
      {showHint && <p className="hint-text">Hint: {question.hint}</p>}

      <div className="options">
        {question.options.map((opt) => (
          <button
            key={opt.term_id}
            className={
              "option-btn " +
              (selectedOptionId === opt.term_id ? "option-selected" : "")
            }
            onClick={() => setSelectedOptionId(opt.term_id)}
          >
            {opt.term}
          </button>
        ))}
      </div>

      <div className="game-actions">
        <button onClick={submitAnswer} disabled={!selectedOptionId}>
          Submit Answer
        </button>
        <button onClick={startGame}>Next Question</button>
      </div>

      {answerResult && (
        <div className="answer-result">
          <p>{answerResult.message}</p>
          <p>
            <strong>Score:</strong> {answerResult.new_score}
          </p>
          <pre>{answerResult.explanation}</pre>
        </div>
      )}
    </div>
  );
}

function DashboardView({ stats }) {
  if (!stats) {
    return <p>Play some questions to see your stats.</p>;
  }

  return (
    <div className="stats">
      <h2>Your Dashboard</h2>
      <p>Total questions: {stats.total_questions}</p>
      <p>Correct answers: {stats.correct_answers}</p>
      <p>Accuracy: {stats.accuracy}%</p>
      <p>Total points: {stats.total_points}</p>
    </div>
  );
}

export default App;

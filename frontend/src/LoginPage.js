import React, { useState } from "react";
import axios from "axios";
import {useNavigate} from "react-router-dom";

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await axios.post("/api/login/", {
        username,
        password,
      });

      localStorage.setItem("access", response.data.access);
      localStorage.setItem("refresh", response.data.refresh);
      axios.defaults.headers.common["Authorization"] = `Bearer ${response.data.access}`;
      setLoading(false);
      onLogin();
    } catch (err) {
      setLoading(false);
      setError("Неверный логин или пароль");
    }
  };

  return (
    <div className="login-page">
      <h2>Вход</h2>
      <form onSubmit={handleLogin} className="login-form">
        <label>
          Логин:
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoFocus
          />
        </label>

        <label>
          Пароль:
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        {error && <p className="error-message">{error}</p>}

        <button type="submit" disabled={loading} className="btn btn-login-submit">
          {loading ? "Вход..." : "Войти"}
        </button>
      </form>

      <p>
        Нет аккаунта?{" "}
        <button type="button" className="btn btn-link-register" onClick={() => navigate("/register")}>
          Зарегистрироваться
        </button>
      </p>
    </div>
  );
}

export default LoginPage;
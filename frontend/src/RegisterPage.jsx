import React, { useState } from "react";
import axios from "axios";
import {useNavigate} from "react-router-dom";

function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await axios.post("/api/register/", {
        username,
        password,
      });
      setLoading(false);
      alert("Регистрация прошла успешно! Теперь можно войти.");
      navigate("/login");
    } catch (err) {
      setLoading(false);
      if (err.response && err.response.data) {
        setError(err.response.data.detail || "Ошибка регистрации");
      } else {
        setError("Ошибка регистрации");
      }
    }
  };

  return (
    <div className="register-page">
      <h2>Регистрация</h2>
      <form onSubmit={handleRegister} className="register-form">
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

        <button type="submit" disabled={loading} className="btn btn-register-submit">
          {loading ? "Регистрация..." : "Зарегистрироваться"}
        </button>
      </form>
    </div>
  );
}

export default RegisterPage;
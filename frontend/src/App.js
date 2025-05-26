import React, { useEffect, useState } from "react";
import axios from "axios";
import TaskList from "./TaskList";
import "./App.css";
import LoginPage from "./LoginPage";
import RegisterPage from "./RegisterPage";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

function App() {
  const [tasks, setTasks] = useState([]);
  const [pagination, setPagination] = useState({ next: null, previous: null });
  const [url, setUrl] = useState("/api/tasks/");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [deadline, setDeadline] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [ordering, setOrdering] = useState("deadline");
  const [selectedTask, setSelectedTask] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editDeadline, setEditDeadline] = useState("");
  const [editPriority, setEditPriority] = useState("Medium");
  const [saveError, setSaveError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  const buildUrl = () => {
    const params = new URLSearchParams();
    if (statusFilter) params.append("status", statusFilter);
    if (priorityFilter) params.append("priority", priorityFilter);
    if (ordering) params.append("ordering", ordering);
    return `/api/tasks/?${params.toString()}`;
  };

  const fetchTasks = async (customUrl = null) => {
    if (!customUrl) {
      customUrl = buildUrl();
    }
    const res = await axios.get(customUrl);
    setTasks(res.data.results || res.data);
    setPagination({ next: res.data.next, previous: res.data.previous });
    setUrl(customUrl);
  };

  const fetch = async (customUrl = url) => {
    const res = await axios.get(customUrl);
    setTasks(res.data.results || res.data);
    setPagination({ next: res.data.next, previous: res.data.previous });
    setUrl(customUrl);
  };

  const createTask = async () => {
    if (!title.trim()) return;
    await axios.post("/api/tasks/", {
      title,
      description,
      deadline: deadline ? deadline : null,
      priority,
    });
    setTitle("");
    setDescription("");
    setDeadline("");
    setPriority("Medium");
    await fetch("/api/tasks/");
  };

  const deleteTask = async (id) => {
    await axios.delete(`/api/tasks/${id}/`);
    await fetchTasks();
  };

  const toggleComplete = async (task) => {
    const isCompletedLike = task.status === "Completed" || task.status === "Late";
    const url = `/api/tasks/${task.id}/${isCompletedLike ? "uncomplete" : "complete"}/`;
    await axios.post(url);
    await fetchTasks();
  };

  const loadTaskDetails = async (taskId) => {
    setModalLoading(true);
    setModalError(null);
    try {
      const res = await axios.get(`/api/tasks/${taskId}/`);
      setSelectedTask(res.data);
      setModalVisible(true);
    } catch (error) {
      setModalError("Ошибка загрузки данных задачи");
    } finally {
      setModalLoading(false);
    }
  };

  const onTaskClick = (task) => {
    loadTaskDetails(task.id);
  };

  const closeModal = () => {
    setModalVisible(false);
    setSelectedTask(null);
  };

  const startEditing = () => {
    if (!selectedTask) return;
    setEditTitle(selectedTask.title || "");
    setEditDescription(selectedTask.description || "");
    setEditDeadline(selectedTask.deadline ? selectedTask.deadline.slice(0, 10) : "");
    setEditPriority(selectedTask.priority || "Medium");
    setIsEditing(true);
    setSaveError(null);
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setSaveError(null);
  };

  const saveChanges = async () => {
    setSaveError(null);
    setSaving(true);
    try {
      await axios.put(`/api/tasks/${selectedTask.id}/`, {
        title: editTitle,
        description: editDescription,
        deadline: editDeadline || null,
        priority: editPriority,
      });
      setSelectedTask(prev => ({
        ...prev,
        title: editTitle,
        description: editDescription,
        deadline: editDeadline,
        priority: editPriority,
      }));
      setIsEditing(false);
      await fetchTasks();
    } catch (error) {
      setSaveError("Ошибка при сохранении изменений");
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      (async () => {
        await fetchTasks();
      })();
    } else {
      setTasks([]);
    }
  }, [statusFilter, priorityFilter, ordering, isAuthenticated]);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      setIsAuthenticated(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    delete axios.defaults.headers.common["Authorization"];
    setIsAuthenticated(false);
    setShowRegister(false);
  };

  const toggleRegister = () => {
    setShowRegister((prev) => !prev);
  };

  if (!isAuthenticated) {
    return (
      <Router>
        <Routes>
          <Route
            path="/login"
            element={<LoginPage onLogin={handleLoginSuccess} />}
          />
          <Route path="/register" element={<RegisterPage onRegister={() => window.location.href = "/login"} />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    );
  }

  return (
    <Router>
      <div className="app-container">
        <button onClick={handleLogout} className="btn btn-logout">
          Выйти
        </button>
        <h1 className="app-title">To Do</h1>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            await createTask();
          }}
          className="task-form"
        >
          <input
            type="text"
            className="input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Название задачи"
            required
          />
          <textarea
            className="input textarea"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Описание задачи"
            rows={3}
          />
          <div className="form-row">
            <input
              type="date"
              className="input"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
            />
            <select
              className="input select"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
            >
              <option value="Low">Низкий</option>
              <option value="Medium">Средний</option>
              <option value="High">Высокий</option>
              <option value="Critical">Критический</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary">
            Добавить задачу
          </button>
        </form>

        <div className="filters">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Все статусы</option>
            <option value="Active">Активные</option>
            <option value="Completed">Завершённые</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="">Все приоритеты</option>
            <option value="Low">Низкий</option>
            <option value="Medium">Средний</option>
            <option value="High">Высокий</option>
            <option value="Critical">Критический</option>
          </select>

          <select
            value={ordering}
            onChange={(e) => setOrdering(e.target.value)}
          >
            <option value="deadline">Сортировать по сроку</option>
            <option value="created_at">Сортировать по дате создания</option>
            <option value="id">Сортировать по ID</option>
            <option value="-deadline">По сроку (обратный порядок)</option>
            <option value="-created_at">По дате создания (обратный порядок)</option>
            <option value="-id">По ID (обратный порядок)</option>
          </select>
        </div>

        <div className="tasklist-container">
          <TaskList
            tasks={tasks}
            onDelete={deleteTask}
            onToggleComplete={toggleComplete}
            onTaskClick={onTaskClick}
          />
        </div>

        <div className="pagination">
          <button
            onClick={() => pagination.previous && fetchTasks(pagination.previous)}
            className="btn"
            disabled={!pagination.previous}
          >
            ← Назад
          </button>
          <button
            onClick={() => pagination.next && fetchTasks(pagination.next)}
            className="btn"
            disabled={!pagination.next}
          >
            Вперёд →
          </button>
        </div>

        {modalVisible && (
      <div className="modal-backdrop" onClick={closeModal}>
        <div
          className="modal-content"
          onClick={(e) => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          tabIndex={-1}
        >
          <button className="modal-close-btn" onClick={closeModal} aria-label="Закрыть окно">
            &times;
          </button>

          {modalLoading ? (
                <p className="modal-loading">Загрузка...</p>
                ) : modalError ? (
                  <p className="modal-error">{modalError}</p>
                ) : (
                  <>
                    {!isEditing ? (
                      <>
                        <h2 id="modal-title">{selectedTask.title}</h2>
                        <div className="modal-body">
                          <p><strong>Описание:</strong> {selectedTask.description || "Нет описания"}</p>
                          <p><strong>Приоритет:</strong> {selectedTask.priority}</p>
                          <p><strong>Статус:</strong> {selectedTask.status}</p>
                          <p><strong>Дедлайн:</strong> {selectedTask.deadline ? new Date(selectedTask.deadline).toLocaleDateString("ru-RU") : "Нет"}</p>
                          <p><strong>Дата создания:</strong> {selectedTask.created_at ? new Date(selectedTask.created_at).toLocaleString("ru-RU") : "Нет данных"}</p>
                          <p><strong>Дата изменения:</strong> {selectedTask.updated_at ? new Date(selectedTask.updated_at).toLocaleString("ru-RU") : "Нет данных"}</p>
                        </div>
                        <div className="modal-footer">
                          <button className="modal-edit-button" onClick={startEditing}>
                            Редактировать
                          </button>
                        </div>
                      </>
                    ) : (
                        <div className="modal-edit-form">
                        <h2 id="modal-title">Редактировать задачу</h2>
                        <label>
                          Название:
                          <input
                            type="text"
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            required
                          />
                        </label>
                        <label>
                          Описание:
                          <textarea
                            value={editDescription}
                            onChange={(e) => setEditDescription(e.target.value)}
                            rows={3}
                          />
                        </label>
                        <label>
                          Дедлайн:
                          <input
                            type="date"
                            value={editDeadline}
                            onChange={(e) => setEditDeadline(e.target.value)}
                          />
                        </label>
                        <label>
                          Приоритет:
                          <select
                            value={editPriority}
                            onChange={(e) => setEditPriority(e.target.value)}
                          >
                            <option value="Low">Низкий</option>
                            <option value="Medium">Средний</option>
                            <option value="High">Высокий</option>
                            <option value="Critical">Критический</option>
                          </select>
                        </label>

                        {saveError && <p className="modal-error">{saveError}</p>}

                        <div className="modal-buttons">
                          <button
                            className="btn btn-primary"
                            onClick={saveChanges}
                            disabled={saving}
                          >
                            {saving ? "Сохранение..." : "Сохранить"}
                          </button>
                          <button
                            className="btn btn-secondary"
                            onClick={cancelEditing}
                            disabled={saving}
                          >
                            Отмена
                          </button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}
      </div>
    </Router>
  );
}

export default App;
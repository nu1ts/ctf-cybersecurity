import React from "react";
import "./App.css";

const TaskList = ({ tasks, onDelete, onToggleComplete, onTaskClick  }) => {
  if (!tasks.length) return <p className="empty-message">Задачи отсутствуют</p>;

  const formatDeadline = (deadline) => {
    if (!deadline) return "Нет дедлайна";
    const dateObj = new Date(deadline);
    return dateObj.toLocaleDateString("ru-RU");
  };

  const getDeadlineClass = (task) => {
    if (task.status === "Completed" || task.status === "Late") return "task-completed";

    if (!task.deadline) return "";

    const now = new Date();
    const deadlineDate = new Date(task.deadline);

    const diffMs = deadlineDate - now;
    const diffDays = diffMs / (1000 * 60 * 60 * 24);

    if (diffDays < 0) {
      return "task-overdue";
    } else if (diffDays <= 3) {
      return "task-soon";
    }

    return "";
  };

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <li
          key={task.id}
          className={`task-item ${getDeadlineClass(task)} ${
            task.status === "Completed" || task.status === "Late" ? "completed" : ""
          }`}
        >
          <div className="task-content"
               onClick={() => onTaskClick(task)}
               title="Просмотреть детали задачи"
          >
            <h3 className="task-title">{task.title}</h3>
            <p className="task-description">{task.description}</p>
            <p className="task-meta">
              Приоритет: <span>{task.priority}</span>
            </p>
            <p className="task-meta">
              Дедлайн: <span>{formatDeadline(task.deadline)}</span>
            </p>
          </div>

          {task.status === "Completed" || task.status === "Late" ? (
            <button
              onClick={() => onToggleComplete(task)}
              className="btn btn-uncomplete"
              title="Отменить выполнение"
            >
              Отменить
            </button>
          ) : (
            <button
              onClick={() => onToggleComplete(task)}
              className="btn btn-complete"
              title="Отметить как выполненную"
            >
              Выполнить
            </button>
          )}

          <button
            onClick={() => onDelete(task.id)}
            className="btn btn-delete"
            title="Удалить задачу"
          >
            &times;
          </button>
        </li>
      ))}
    </ul>
  );
};

export default TaskList;
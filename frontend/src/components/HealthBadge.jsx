import { useEffect, useState } from "react";
import { API_BASE_URL, getHealth } from "../lib/api";

export function HealthBadge() {
  const [status, setStatus] = useState("checking");
  const [message, setMessage] = useState("Checking backend");

  useEffect(() => {
    let active = true;
    getHealth()
      .then((payload) => {
        if (!active) {
          return;
        }
        setStatus("online");
        setMessage(payload.status || "healthy");
      })
      .catch((error) => {
        if (!active) {
          return;
        }
        setStatus("offline");
        setMessage(error.message);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="health-card">
      <span className={`status-dot ${status}`} />
      <div>
        <p className="health-title">Backend</p>
        <p className="health-message">{message}</p>
        <code className="health-url">{API_BASE_URL}</code>
      </div>
    </section>
  );
}

import { useState } from "react";

export default function App() {
  const [form, setForm] = useState({
    incident_type: "",
    brand: "",
    plate_vats: "",
    plate_ref: "",
    location: "",
    problem_desc: "",
    notes: "",
  });
  const [status, setStatus] = useState(null);

  const sendForm = async () => {
    const res = await fetch("https://your-backend.timeweb.cloud/api/create_ticket", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    setStatus(data);
  };

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  return (
    <div className="p-4 text-center">
      <h2 className="text-xl font-bold mb-2">Создание заявки</h2>

      <select name="incident_type" onChange={handleChange} className="border p-1 mb-2 w-full">
        <option value="">Тип происшествия</option>
        <option value="ДТП">ДТП</option>
        <option value="Поломка">Поломка</option>
      </select>

      <select name="brand" onChange={handleChange} className="border p-1 mb-2 w-full">
        <option value="">Марка ВАТС</option>
        <option value="Sitrak">Sitrak</option>
        <option value="Kia Ceed">Kia Ceed</option>
      </select>

      <input name="plate_vats" placeholder="Госномер ВАТС" onChange={handleChange} className="border p-1 mb-2 w-full" />
      <input name="plate_ref" placeholder="Госномер прицепа" onChange={handleChange} className="border p-1 mb-2 w-full" />
      <input name="location" placeholder="Местоположение" onChange={handleChange} className="border p-1 mb-2 w-full" />
      <textarea name="problem_desc" placeholder="Описание проблемы" onChange={handleChange} className="border p-1 mb-2 w-full" />
      <input name="notes" placeholder="Примечание" onChange={handleChange} className="border p-1 mb-2 w-full" />

      <button onClick={sendForm} className="bg-blue-500 text-white px-4 py-2 rounded">
        Отправить
      </button>

      {status && (
        <div className="mt-4">
          {status.success ? (
            <p>✅ Создано в Jira: {status.jira_key}</p>
          ) : (
            <pre className="text-red-500">{status.error}</pre>
          )}
        </div>
      )}
    </div>
  );
}

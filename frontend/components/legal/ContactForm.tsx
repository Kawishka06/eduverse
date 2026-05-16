"use client";

import { FormEvent, useState } from "react";
import { submitContactForm } from "@/lib/api";

const CATEGORIES = [
  { value: "general", label: "General inquiry" },
  { value: "support", label: "Technical support" },
  { value: "billing", label: "Billing" },
  { value: "legal", label: "Legal / privacy" },
  { value: "dmca", label: "DMCA / copyright" },
  { value: "other", label: "Other" },
] as const;

const inputClass =
  "mt-1.5 w-full rounded-xl border border-zinc-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 dark:border-zinc-700 dark:bg-zinc-900";

export default function ContactForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [category, setCategory] = useState<string>("general");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">(
    "idle",
  );
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setStatus("loading");
    setError(null);
    try {
      await submitContactForm({
        name: name.trim(),
        email: email.trim(),
        subject: subject.trim(),
        message: message.trim(),
        category,
      });
      setStatus("success");
      setName("");
      setEmail("");
      setSubject("");
      setMessage("");
      setCategory("general");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Could not send message");
    }
  }

  if (status === "success") {
    return (
      <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center dark:border-emerald-900 dark:bg-emerald-950/40">
        <p className="text-lg font-semibold text-emerald-900 dark:text-emerald-100">
          Message sent
        </p>
        <p className="mt-2 text-sm text-emerald-800 dark:text-emerald-200">
          Thank you. Your submission was saved and our team will follow up by email.
        </p>
        <button
          type="button"
          onClick={() => setStatus("idle")}
          className="mt-4 text-sm font-medium text-violet-600 hover:underline"
        >
          Send another message
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
          Name
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={inputClass}
            maxLength={120}
          />
        </label>
        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={inputClass}
          />
        </label>
      </div>
      <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
        Category
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className={inputClass}
        >
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
        Subject
        <input
          required
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className={inputClass}
          maxLength={200}
        />
      </label>
      <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
        Message
        <textarea
          required
          rows={5}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className={`${inputClass} resize-y`}
          minLength={10}
          maxLength={5000}
          placeholder="How can we help?"
        />
      </label>
      {error && (
        <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/50">
          {error}
        </p>
      )}
      <button
        type="submit"
        disabled={status === "loading"}
        className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 py-3 text-sm font-semibold text-white disabled:opacity-50"
      >
        {status === "loading" ? "Sending…" : "Send message"}
      </button>
    </form>
  );
}

import Link from "next/link";
import type { ReactNode } from "react";

export default function LegalPageShell({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <main className="mx-auto max-w-4xl px-4 py-12 md:py-16">
      <Link
        href="/"
        className="text-sm font-medium text-violet-600 hover:underline"
      >
        ← Back to home
      </Link>
      <h1 className="mt-6 text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
        {title}
      </h1>
      <div className="mt-8">{children}</div>
    </main>
  );
}

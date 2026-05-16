import Link from "next/link";

const legalLinks = [
  { href: "/privacy", label: "Privacy Policy" },
  { href: "/terms", label: "Terms & Conditions" },
  { href: "/dmca", label: "DMCA" },
  { href: "/contact", label: "Contact Us" },
] as const;

export default function SiteFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-auto border-t border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-8 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-zinc-500">
          © {year} EduVerse AI. All rights reserved.
        </p>
        <nav className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {legalLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-zinc-600 hover:text-violet-600 dark:text-zinc-400 dark:hover:text-violet-400"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}

import ContactForm from "@/components/legal/ContactForm";
import LegalPageShell from "@/components/legal/LegalPageShell";
import { contactInfo } from "@/lib/legal-content";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Contact Us — EduVerse AI",
};

export default function ContactPage() {
  return (
    <LegalPageShell title="Contact Us">
      <p className="mb-6 text-zinc-600 dark:text-zinc-400">
        Questions, support, legal notices, or DMCA requests — send us a message.{" "}
        {contactInfo.responseTime}
      </p>
      <div className="mb-8 grid gap-4 text-sm sm:grid-cols-3">
        <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
          <p className="font-semibold">Support</p>
          <a
            href={`mailto:${contactInfo.supportEmail}`}
            className="mt-1 block text-violet-600 hover:underline"
          >
            {contactInfo.supportEmail}
          </a>
        </div>
        <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
          <p className="font-semibold">Legal / privacy</p>
          <a
            href={`mailto:${contactInfo.legalEmail}`}
            className="mt-1 block text-violet-600 hover:underline"
          >
            {contactInfo.legalEmail}
          </a>
        </div>
        <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
          <p className="font-semibold">DMCA</p>
          <a
            href={`mailto:${contactInfo.dmcaEmail}`}
            className="mt-1 block text-violet-600 hover:underline"
          >
            {contactInfo.dmcaEmail}
          </a>
        </div>
      </div>
      <ContactForm />
      <p className="mt-6 text-sm text-zinc-500">
        For copyright claims, see our{" "}
        <Link href="/dmca" className="text-violet-600 hover:underline">
          DMCA policy
        </Link>
        .
      </p>
    </LegalPageShell>
  );
}

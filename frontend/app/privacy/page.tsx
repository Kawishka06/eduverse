import LegalDocumentView from "@/components/legal/LegalDocumentView";
import LegalPageShell from "@/components/legal/LegalPageShell";
import { privacyPolicy } from "@/lib/legal-content";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy — EduVerse AI",
};

export default function PrivacyPage() {
  return (
    <LegalPageShell title={privacyPolicy.title}>
      <LegalDocumentView doc={privacyPolicy} />
    </LegalPageShell>
  );
}

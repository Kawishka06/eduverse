import LegalDocumentView from "@/components/legal/LegalDocumentView";
import LegalPageShell from "@/components/legal/LegalPageShell";
import { termsOfService } from "@/lib/legal-content";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms & Conditions — EduVerse AI",
};

export default function TermsPage() {
  return (
    <LegalPageShell title={termsOfService.title}>
      <LegalDocumentView doc={termsOfService} />
    </LegalPageShell>
  );
}

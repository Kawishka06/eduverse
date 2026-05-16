import LegalDocumentView from "@/components/legal/LegalDocumentView";
import LegalPageShell from "@/components/legal/LegalPageShell";
import { dmcaPolicy } from "@/lib/legal-content";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DMCA Policy — EduVerse AI",
};

export default function DmcaPage() {
  return (
    <LegalPageShell title={dmcaPolicy.title}>
      <LegalDocumentView doc={dmcaPolicy} />
    </LegalPageShell>
  );
}

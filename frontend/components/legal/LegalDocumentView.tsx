import type { LegalDocument } from "@/lib/legal-content";

export default function LegalDocumentView({ doc }: { doc: LegalDocument }) {
  return (
    <article className="prose prose-zinc mx-auto max-w-3xl dark:prose-invert">
      <p className="text-sm text-zinc-500">Last updated: {doc.updated}</p>
      <p className="lead">{doc.intro}</p>
      {doc.sections.map((section) => (
        <section key={section.id} id={section.id}>
          <h2>{section.title}</h2>
          {section.paragraphs.map((p) => (
            <p key={p.slice(0, 40)}>{p}</p>
          ))}
          {section.list && (
            <ul>
              {section.list.map((item) => (
                <li key={item.slice(0, 40)}>{item}</li>
              ))}
            </ul>
          )}
        </section>
      ))}
    </article>
  );
}

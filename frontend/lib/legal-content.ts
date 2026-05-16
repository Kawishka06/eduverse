export type LegalSection = {
  id: string;
  title: string;
  paragraphs: string[];
  list?: string[];
};

export type LegalDocument = {
  title: string;
  updated: string;
  intro: string;
  sections: LegalSection[];
};

export const privacyPolicy: LegalDocument = {
  title: "Privacy Policy",
  updated: "May 16, 2026",
  intro:
    "EduVerse AI (“EduVerse”, “we”, “us”) respects your privacy. This policy explains what we collect, how we use it, and your choices when you use our learning platform.",
  sections: [
    {
      id: "collect",
      title: "Information we collect",
      paragraphs: [
        "Account information such as your name, email address, and profile details when you register.",
        "Content you create, including posts, comments, meme prompts, tutor questions, and uploaded avatars.",
        "Usage data such as device type, browser, pages visited, and interactions with AI features.",
        "Technical logs used for security, abuse prevention, and service reliability.",
      ],
    },
    {
      id: "use",
      title: "How we use information",
      paragraphs: ["We use your information to:"],
      list: [
        "Provide and improve EduVerse features (community feed, AI tutor, meme studio, presentations).",
        "Authenticate you and enforce community guidelines, including content moderation.",
        "Respond to support requests submitted through our contact form.",
        "Comply with legal obligations and protect the safety of our users.",
      ],
    },
    {
      id: "ai",
      title: "AI and third-party services",
      paragraphs: [
        "AI features may send your prompts to third-party providers (for example, fal.ai) to generate images or text. Do not submit sensitive personal data in prompts.",
        "We use Supabase for authentication and data storage. Please review their policies for infrastructure processing.",
      ],
    },
    {
      id: "rights",
      title: "Your rights",
      paragraphs: [
        "Depending on your location, you may request access, correction, export, or deletion of your account data. Use Settings → Export my data / Delete account, or contact us.",
        "Parents or schools using EduVerse with minors should ensure appropriate consent under applicable law (including FERPA/COPPA where relevant).",
      ],
    },
    {
      id: "contact",
      title: "Contact",
      paragraphs: [
        "Questions about this policy: use our Contact page or email privacy@eduverse.app (replace with your official address before production).",
      ],
    },
  ],
};

export const termsOfService: LegalDocument = {
  title: "Terms and Conditions",
  updated: "May 16, 2026",
  intro:
    "By accessing or using EduVerse AI, you agree to these Terms. If you do not agree, do not use the service.",
  sections: [
    {
      id: "eligibility",
      title: "Eligibility",
      paragraphs: [
        "You must be at least 13 years old (or the minimum age in your jurisdiction) to create an account. Users under 18 should use EduVerse with parental or school authorization.",
      ],
    },
    {
      id: "accounts",
      title: "Accounts and conduct",
      paragraphs: ["You are responsible for your account credentials and all activity under your account."],
      list: [
        "Do not harass, threaten, or post unlawful, hateful, or sexually explicit content.",
        "Do not attempt to bypass security, scrape the service, or abuse AI rate limits.",
        "Do not upload content you do not have rights to share.",
        "Repeated violations may result in warnings, suspension, or termination.",
      ],
    },
    {
      id: "content",
      title: "User content and license",
      paragraphs: [
        "You retain ownership of content you post. You grant EduVerse a non-exclusive license to host, display, and process your content solely to operate the platform.",
        "AI-generated outputs may not be unique; you are responsible for how you use generated memes or study materials.",
      ],
    },
    {
      id: "disclaimer",
      title: "Disclaimer",
      paragraphs: [
        "EduVerse is provided “as is” for educational purposes. AI answers may be inaccurate. We do not guarantee uninterrupted service.",
      ],
    },
    {
      id: "liability",
      title: "Limitation of liability",
      paragraphs: [
        "To the fullest extent permitted by law, EduVerse and its operators are not liable for indirect, incidental, or consequential damages arising from use of the service.",
      ],
    },
  ],
};

export const dmcaPolicy: LegalDocument = {
  title: "DMCA Copyright Policy",
  updated: "May 16, 2026",
  intro:
    "EduVerse respects intellectual property rights and responds to notices of alleged copyright infringement under the Digital Millennium Copyright Act (DMCA).",
  sections: [
    {
      id: "agent",
      title: "Designated agent",
      paragraphs: [
        "Send DMCA notices to: DMCA Agent, EduVerse AI — legal@eduverse.app (replace with your legal contact before production).",
        "Include your physical address and phone number in production deployments.",
      ],
    },
    {
      id: "notice",
      title: "Required notice elements",
      paragraphs: ["Your written notice must include:"],
      list: [
        "Identification of the copyrighted work claimed to have been infringed.",
        "Identification of the material on EduVerse and information reasonably sufficient to locate it (URL or post ID).",
        "Your contact information and a statement of good faith belief that use is not authorized.",
        "A statement, under penalty of perjury, that the information is accurate and you are authorized to act.",
        "Your physical or electronic signature.",
      ],
    },
    {
      id: "counter",
      title: "Counter-notification",
      paragraphs: [
        "If you believe content was removed in error, you may submit a counter-notification with the elements required by 17 U.S.C. §512(g). We may restore content unless the complainant seeks court action.",
      ],
    },
    {
      id: "repeat",
      title: "Repeat infringers",
      paragraphs: [
        "We may terminate accounts of users who are repeat infringers in appropriate circumstances.",
      ],
    },
  ],
};

export const contactInfo = {
  supportEmail: "support@eduverse.app",
  legalEmail: "legal@eduverse.app",
  dmcaEmail: "dmca@eduverse.app",
  responseTime: "We aim to respond within 2–3 business days.",
};

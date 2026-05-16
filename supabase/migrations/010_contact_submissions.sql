-- Contact form submissions from the public Contact Us page
CREATE TABLE IF NOT EXISTS contact_submissions (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID REFERENCES profiles (id) ON DELETE SET NULL,
  name       TEXT NOT NULL CHECK (char_length(trim(name)) >= 1),
  email      TEXT NOT NULL CHECK (char_length(trim(email)) >= 3),
  subject    TEXT NOT NULL CHECK (char_length(trim(subject)) >= 1),
  category   TEXT NOT NULL DEFAULT 'general'
    CHECK (category IN ('general', 'support', 'billing', 'legal', 'dmca', 'other')),
  message    TEXT NOT NULL CHECK (char_length(trim(message)) >= 10 AND char_length(message) <= 5000),
  status     TEXT NOT NULL DEFAULT 'new'
    CHECK (status IN ('new', 'read', 'resolved')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contact_submissions_created
  ON contact_submissions (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_contact_submissions_status
  ON contact_submissions (status, created_at DESC);

ALTER TABLE contact_submissions ENABLE ROW LEVEL SECURITY;

NOTIFY pgrst, 'reload schema';

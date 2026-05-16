-- EduVerse — Lesson features (run once in Supabase SQL Editor)
-- Combines migrations 007 + 008. Safe to re-run.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Required by triggers below (no-op if already from migration 001)
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========== 007_lesson_agent_tables.sql ==========

DO $$ BEGIN
  CREATE TYPE character_visibility AS ENUM ('personal', 'class');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE lesson_job_status AS ENUM ('pending', 'processing', 'completed', 'failed');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS lesson_characters (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id            UUID NOT NULL REFERENCES profiles (id) ON DELETE CASCADE,
  name                TEXT NOT NULL,
  personality         TEXT NOT NULL DEFAULT '',
  teaching_style      TEXT NOT NULL DEFAULT '',
  visual_description  TEXT NOT NULL DEFAULT '',
  voice_style         TEXT NOT NULL DEFAULT 'friendly',
  character_bible     TEXT,
  reference_image_url TEXT,
  reference_sheet_urls TEXT[] NOT NULL DEFAULT '{}',
  class_tag           TEXT,
  visibility          character_visibility NOT NULL DEFAULT 'personal',
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lesson_characters_owner ON lesson_characters (owner_id);
CREATE INDEX IF NOT EXISTS idx_lesson_characters_visibility ON lesson_characters (visibility);

CREATE TABLE IF NOT EXISTS lesson_materials (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles (id) ON DELETE CASCADE,
  filename        TEXT NOT NULL,
  content_type    TEXT NOT NULL,
  storage_path    TEXT NOT NULL,
  file_url        TEXT NOT NULL,
  extracted_text  TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lesson_materials_user ON lesson_materials (user_id);

CREATE TABLE IF NOT EXISTS lesson_video_jobs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles (id) ON DELETE CASCADE,
  material_id     UUID REFERENCES lesson_materials (id) ON DELETE SET NULL,
  character_id    UUID REFERENCES lesson_characters (id) ON DELETE SET NULL,
  status          lesson_job_status NOT NULL DEFAULT 'pending',
  progress        INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  title           TEXT NOT NULL DEFAULT '',
  scenes_json     JSONB NOT NULL DEFAULT '[]'::jsonb,
  playlist_url    TEXT,
  error_message   TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lesson_video_jobs_user ON lesson_video_jobs (user_id);

DROP TRIGGER IF EXISTS lesson_characters_updated_at ON lesson_characters;
CREATE TRIGGER lesson_characters_updated_at
  BEFORE UPDATE ON lesson_characters
  FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

DROP TRIGGER IF EXISTS lesson_video_jobs_updated_at ON lesson_video_jobs;
CREATE TRIGGER lesson_video_jobs_updated_at
  BEFORE UPDATE ON lesson_video_jobs
  FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

ALTER TABLE lesson_characters ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_video_jobs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "lesson_characters_select" ON lesson_characters;
CREATE POLICY "lesson_characters_select"
  ON lesson_characters FOR SELECT
  USING (owner_id = auth.uid() OR visibility = 'class');

DROP POLICY IF EXISTS "lesson_characters_insert_own" ON lesson_characters;
CREATE POLICY "lesson_characters_insert_own"
  ON lesson_characters FOR INSERT
  WITH CHECK (owner_id = auth.uid());

DROP POLICY IF EXISTS "lesson_characters_update_own" ON lesson_characters;
CREATE POLICY "lesson_characters_update_own"
  ON lesson_characters FOR UPDATE
  USING (owner_id = auth.uid());

DROP POLICY IF EXISTS "lesson_characters_delete_own" ON lesson_characters;
CREATE POLICY "lesson_characters_delete_own"
  ON lesson_characters FOR DELETE
  USING (owner_id = auth.uid());

DROP POLICY IF EXISTS "lesson_materials_select_own" ON lesson_materials;
CREATE POLICY "lesson_materials_select_own"
  ON lesson_materials FOR SELECT
  USING (user_id = auth.uid());

DROP POLICY IF EXISTS "lesson_materials_insert_own" ON lesson_materials;
CREATE POLICY "lesson_materials_insert_own"
  ON lesson_materials FOR INSERT
  WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS "lesson_materials_delete_own" ON lesson_materials;
CREATE POLICY "lesson_materials_delete_own"
  ON lesson_materials FOR DELETE
  USING (user_id = auth.uid());

DROP POLICY IF EXISTS "lesson_video_jobs_select_own" ON lesson_video_jobs;
CREATE POLICY "lesson_video_jobs_select_own"
  ON lesson_video_jobs FOR SELECT
  USING (user_id = auth.uid());

DROP POLICY IF EXISTS "lesson_video_jobs_insert_own" ON lesson_video_jobs;
CREATE POLICY "lesson_video_jobs_insert_own"
  ON lesson_video_jobs FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- ========== 008_lesson_storage_buckets.sql ==========

INSERT INTO storage.buckets (id, name, public)
VALUES ('lesson-materials', 'lesson-materials', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public)
VALUES ('lesson-characters', 'lesson-characters', true)
ON CONFLICT (id) DO NOTHING;

DROP POLICY IF EXISTS "lesson_materials_public_read" ON storage.objects;
CREATE POLICY "lesson_materials_public_read"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'lesson-materials');

DROP POLICY IF EXISTS "lesson_materials_user_upload" ON storage.objects;
CREATE POLICY "lesson_materials_user_upload"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'lesson-materials'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

DROP POLICY IF EXISTS "lesson_materials_user_delete" ON storage.objects;
CREATE POLICY "lesson_materials_user_delete"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'lesson-materials'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

DROP POLICY IF EXISTS "lesson_characters_public_read" ON storage.objects;
CREATE POLICY "lesson_characters_public_read"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'lesson-characters');

DROP POLICY IF EXISTS "lesson_characters_user_upload" ON storage.objects;
CREATE POLICY "lesson_characters_user_upload"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'lesson-characters'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

DROP POLICY IF EXISTS "lesson_characters_user_delete" ON storage.objects;
CREATE POLICY "lesson_characters_user_delete"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'lesson-characters'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- Verify
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('lesson_characters', 'lesson_materials', 'lesson_video_jobs');

SELECT id, name, public FROM storage.buckets
WHERE id IN ('lesson-materials', 'lesson-characters');

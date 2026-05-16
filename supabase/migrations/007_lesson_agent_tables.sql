-- Lesson characters, student materials, and lesson video jobs

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

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

-- ---------------------------------------------------------------------------
-- Lesson characters (custom tutor mascots)
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- Uploaded study materials
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- Lesson video generation jobs
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- Triggers
-- ---------------------------------------------------------------------------
DROP TRIGGER IF EXISTS lesson_characters_updated_at ON lesson_characters;
CREATE TRIGGER lesson_characters_updated_at
  BEFORE UPDATE ON lesson_characters
  FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

DROP TRIGGER IF EXISTS lesson_video_jobs_updated_at ON lesson_video_jobs;
CREATE TRIGGER lesson_video_jobs_updated_at
  BEFORE UPDATE ON lesson_video_jobs
  FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

-- ---------------------------------------------------------------------------
-- RLS
-- ---------------------------------------------------------------------------
ALTER TABLE lesson_characters ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_video_jobs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "lesson_characters_select" ON lesson_characters;
CREATE POLICY "lesson_characters_select"
  ON lesson_characters FOR SELECT
  USING (
    owner_id = auth.uid()
    OR visibility = 'class'
  );

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

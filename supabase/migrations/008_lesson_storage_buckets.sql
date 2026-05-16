-- Storage for lesson materials and character reference art

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

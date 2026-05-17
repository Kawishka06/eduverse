/** Parse job id from backend or frontend lesson video URLs. */
export function parseLessonVideoJobId(url: string | null | undefined): string | null {
  if (!url) return null;
  const match = url.match(/lesson-video\/([0-9a-f-]{36})\/file/i);
  return match?.[1] ?? null;
}

export function isLessonVideoContentUrl(url: string | null | undefined): boolean {
  return Boolean(parseLessonVideoJobId(url));
}

export function lessonVideoApiPath(jobId: string): string {
  return `/api/lesson-video/${jobId}/file`;
}

import LessonStudio from "@/components/LessonStudio";

export const metadata = { title: "Lesson Studio — EduVerse" };

export default function LessonStudioPage() {
  return (
    <div className="p-6">
      <h1 className="mb-2 text-2xl font-bold text-zinc-900 dark:text-zinc-50">
        Lesson Studio
      </h1>
      <p className="mb-6 text-sm text-zinc-500">
        Upload study materials and generate a narrated lesson video with your character.
      </p>
      <LessonStudio />
    </div>
  );
}

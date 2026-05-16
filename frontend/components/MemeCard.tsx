"use client";

type MemeCardProps = {
  imageUrl: string;
  topText: string;
  bottomText: string;
  alt?: string;
};

function captionSizeClass(text: string): string {
  const words = text.trim().split(/\s+/).length;
  if (words > 10) return "meme-caption-compact";
  if (words > 7) return "meme-caption-medium";
  return "";
}

export default function MemeCard({
  imageUrl,
  topText,
  bottomText,
  alt = "Generated meme",
}: MemeCardProps) {
  return (
    <div className="meme-card relative mx-auto w-full max-w-lg overflow-hidden rounded-xl bg-black shadow-lg">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={imageUrl} alt={alt} className="block w-full object-cover" />
      {topText ? (
        <p
          className={`meme-caption meme-caption-top ${captionSizeClass(topText)}`}
        >
          {topText}
        </p>
      ) : null}
      {bottomText ? (
        <p
          className={`meme-caption meme-caption-bottom ${captionSizeClass(bottomText)}`}
        >
          {bottomText}
        </p>
      ) : null}
    </div>
  );
}

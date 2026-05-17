import type { PostComment } from "@/lib/api";
import { getBackendOrigin } from "@/lib/api-base";

export type FeedWsMessage =
  | {
      type: "like_update";
      post_id: string;
      likes: number;
      liked: boolean;
      user_id: string;
    }
  | {
      type: "comment_added";
      post_id: string;
      comments: number;
      comment: PostComment;
    }
  | { type: "pong" };

export function feedWebSocketUrl(token: string): string {
  const api = getBackendOrigin();
  const wsBase = api.replace(/^http/, "ws");
  return `${wsBase}/ws/feed?token=${encodeURIComponent(token)}`;
}

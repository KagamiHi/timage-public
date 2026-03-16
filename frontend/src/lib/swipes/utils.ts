import { backend } from "../../api";
import type { ImageData } from "../../types";

export async function fetchImages(): Promise<ImageData[]> {
  const response: [] = await backend.Swipes.get_memes().then(
    (response: any) => response.data(),
  );
  return response;
}

export async function sendReaction(imageId: number, react: boolean) {
  await backend.Swipes.react({
    image_id: imageId,
    body: {
      react: react,
    },
  });
}

export const preloadImage = (url: string): Promise<void> => {
  return new Promise((resolve) => {
    const img = new Image();
    img.src = url;
    img.onload = () => resolve();
  });
};
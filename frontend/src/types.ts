export type ImageData = {
  id: number;
  url: string;
};
  
export class ImageQueue {
  private queue: ImageData[] = [];
  private currentIndex = 0;

  constructor(initialImages: ImageData[] = []) {
    this.queue = initialImages;
  }

  enqueue(images: ImageData[]) {
    this.queue.push(...images);
  }

  getCurrent(): ImageData | null {
    return this.queue[this.currentIndex] || null;
  }

  getCurrentIndex(): number {
    return this.currentIndex;
  }

  next(): ImageData | null {
    if (this.currentIndex < this.queue.length - 1) {
      this.currentIndex++;
      return this.getCurrent();
    }
    return null;
  }

  previous(): ImageData | null {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      return this.getCurrent();
    }
    return null;
  }

  getRemainingCount(): number {
    return Math.max(0, this.queue.length - this.currentIndex - 1);
  }

  length(): number {
    return this.queue.length;
  }

  peekNext(): ImageData | null {
    return this.queue[this.currentIndex + 1] || null;
  }
}
<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { ThumbsUpSolid, ThumbsDownSolid } from "flowbite-svelte-icons";
  import type { ImageData } from "../../types";
  import { ImageQueue } from "../../types";
  import Card from "./Card.svelte";
  import Loading from "./Loading.svelte";
  import SwipeNotification from "./SwipeNotification.svelte";
  import { fetchImages, sendReaction, preloadImage } from "./utils";

  let imageQueue: ImageQueue;
  let currentImage: ImageData | null = $state(null);
  let images: ImageData[] = [];
  let error: string | null = null;
  let promise: Promise<void> | null = $state(null);

  async function handleNext(react: boolean) {
    sendReaction(currentImage!.id, react);
    const nextImage = imageQueue.next();
    if (!nextImage) {
      currentImage = null;
      return;
    }
    currentImage = nextImage;
    promise = preloadImage(currentImage.url);
    if (imageQueue.getRemainingCount() < 3) {
      const newImages = await fetchImages();
      imageQueue.enqueue(newImages);
      await Promise.all(newImages.map((img) => preloadImage(img.url)));
    }
  }

  const init = async () => {
    try {
      images = await fetchImages();
      imageQueue = new ImageQueue(images);
      currentImage = imageQueue.getCurrent();
      if (currentImage) {
        promise = preloadImage(currentImage.url);
      }
      await Promise.all(images.map((img) => preloadImage(img.url)));
    } catch (err) {
      error = err instanceof Error ? err.message : "Unknown error";
    }
  };
  const initPromise = init();

  let touchStartX = 0;

  function handleTouchStart(e: TouchEvent) {
    touchStartX = e.touches?.[0]?.clientX;
  }

  function handleTouchEnd(e: TouchEvent) {
    const touchEndX = e.changedTouches?.[0]?.clientX;
    const deltaX = touchEndX - touchStartX;

    if (Math.abs(deltaX) > 50) {
      // 50px threshold
      handleNext(deltaX > 0);
    }
  }
</script>

<div>
  {#if currentImage}
    {#await promise}
      <Loading />
    {:then _}
      <div class="flex flex-col h-screen">
        <SwipeNotification />
        <div
          class="card"
          role="button"
          tabindex="0"
          ontouchstart={handleTouchStart}
          ontouchend={handleTouchEnd}
        >
          <Card url={currentImage.url} />
        </div>
        <div class="h-[10vh] flex items-center justify-center">
          <div class="flex gap-4">
            <Button
              pill={true}
              outline={true}
              class="p-2!"
              size="lg"
              on:click={() => handleNext(false)}
            >
              <ThumbsDownSolid class="w-6 h-6 text-primary-700" />
            </Button>
            <Button
              pill={true}
              outline={true}
              class="p-2!"
              size="lg"
              on:click={() => handleNext(true)}
            >
              <ThumbsUpSolid class="w-6 h-6 text-primary-700" />
            </Button>
          </div>
        </div>
      </div>
    {/await}
  {:else}
    <p>No more memes for You</p>
  {/if}
</div>

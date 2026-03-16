<script>
  import WebApp from "@twa-dev/sdk";
  import { onMount } from "svelte";

  onMount(() => {
    WebApp.expand();
  });
</script>

<div id="layout">
  <slot />
</div>

<style>
  #layout {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  @media (max-width: 1024px) {
    #layout {
      height: var(--tg-viewport-height, 100vh);
    }
  }
</style>

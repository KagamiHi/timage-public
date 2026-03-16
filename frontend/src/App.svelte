<script lang="ts">
  import "./app.css";
  import { onMount } from "svelte";
  import { Router, Route } from "svelte-routing";
  import { init, isTMA, viewport } from "@telegram-apps/sdk";
  import Swipes from "./lib/swipes/Swipes.svelte";
  import Layout from "./lib/layout/Layout.svelte";

  const my_init = async () => {};
  const initPromise = my_init();

  onMount(async () => {
    if (await isTMA()) {
      init();

      if (viewport.mount.isAvailable()) {
        await viewport.mount();
        viewport.expand();
      }

      if (viewport.requestFullscreen.isAvailable()) {
        await viewport.requestFullscreen();
      }
    }
  });
</script>

<Layout>
  {#await initPromise}
    <span class="loading loading-ring loading-lg"></span>
  {:then _}
    <Router>
      <Route path="/"><Swipes /></Route>
    </Router>
  {:catch err}
    <p>The site is broken.</p>
  {/await}
</Layout>

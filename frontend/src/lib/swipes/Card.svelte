<script lang="ts">
    let { url } = $props();
</script>

<div
    class="w-full h-[75vh] overflow-hidden rounded-md flex justify-center items-center bg-black"
>
    <img src={url} alt="meme" class="max-h-full max-w-full object-contain" />
</div>

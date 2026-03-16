import { writable } from "svelte/store";

export const accessTokenStore = writable(null);
export const refreshTokenStore = writable(null);

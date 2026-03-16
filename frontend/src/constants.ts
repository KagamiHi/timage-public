export const API_HOST_ROOT = import.meta.env.VITE_HOST;
const HOST_PREFIX = import.meta.env.VITE_HOST_PREFIX || "https";
export const API_HOST = `${HOST_PREFIX}://${API_HOST_ROOT}`;

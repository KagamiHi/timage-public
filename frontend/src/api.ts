import forge from "mappersmith";
import { API_HOST } from "./constants";
import { accessTokenStore, refreshTokenStore } from "./stores";
import { get } from "svelte/store";
import WebApp from "@twa-dev/sdk";
import { EncodeJsonMiddleware } from "mappersmith/middleware";


const refreshToken = async () => {
  const refreshTokenEndpoint = `${API_HOST}/api/token/refresh/`;
  const refreshToken = get(refreshTokenStore);
  let accessToken;

  if (refreshToken) {
    const refreshRequestBody = {
      refresh: refreshToken,
    };

    await fetch(refreshTokenEndpoint, {
      method: "POST",
      body: JSON.stringify(refreshRequestBody),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to refresh token.");
        }
        return response.json();
      })
      .then((data) => {
        accessToken = data["access"];
      })
      .catch((_) => {
        // console.error("Refresh token request failed:", error);
      });
  }
  accessToken && accessTokenStore.set(accessToken);
  return accessToken;
};

const obtainToken = async () => {
  const obtainTokenEndpoint = `${API_HOST}/api/tlg-token/`;
  let accessToken;

  const obtainRequestBody = {
    auth_data: WebApp.initData,
  };

  await fetch(obtainTokenEndpoint, {
    method: "POST",
    body: JSON.stringify(obtainRequestBody),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to obtain tokens");
      }
      return response.json();
    })
    .then((data) => {
      refreshTokenStore.set(data["refresh"]);
      accessToken = data["access"];
    })
    .catch((error) => {
      console.error("Obtain tokens request failed:", error);
      throw error;
    });
  accessToken && accessTokenStore.set(accessToken);
  return accessToken;
};

const AccessTokenMiddleware = () => {
  return () => ({
    request(request: any) {
      let accessToken = get(accessTokenStore);
      return Promise.resolve(accessToken)
        .then(async (token) => token || (await refreshToken()) || (await obtainToken()))
        .then((token) => {
          return request.enhance({
            headers: { Authorization: `Bearer ${token}` },
          });
        });
    },
    response(next: any, renew: any) {
      return next().catch((response: any) => {
        if (response.status() === 401) {
          accessTokenStore.set(null);
          return renew();
        }
        return next();
      });
    },
  });
};
const AccessToken = AccessTokenMiddleware();

export const backend = forge({
  clientId: "twa",
  host: API_HOST,
  middleware: [EncodeJsonMiddleware, AccessToken],
  resources: {
    Swipes: {
      get_memes: { path: "api/swipes/" },
      react: { path: "api/swipes/{image_id}/react/", method: "POST" },
    },
  },
});
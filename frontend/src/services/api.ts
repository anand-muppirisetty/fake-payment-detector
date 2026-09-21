import axios from "axios";

// Central Axios instance. Attaches the JWT access token to every request and
// transparently refreshes it once on a 401 before giving up and logging out.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry && !isRefreshing) {
      original._retry = true;
      isRefreshing = true;
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) throw new Error("No refresh token");
        const { data } = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          null,
          { params: { refresh_token: refreshToken } }
        );
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        isRefreshing = false;
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch {
        isRefreshing = false;
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;

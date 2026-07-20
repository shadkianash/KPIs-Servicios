import axios, { InternalAxiosRequestConfig, AxiosResponse } from "axios";

// Construct Axios instance with baseline configurations
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  timeout: 10000, // 10 seconds timeout
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: Attach tracers or generic headers if needed
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Generate or attach common headers here if necessary
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Global error logging and interception
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    // Common error handling block
    if (error.response) {
      console.error(
        `API Error Response [${error.response.status}]:`,
        error.response.data
      );
    } else if (error.request) {
      console.error("API Error Request (no response received):", error.request);
    } else {
      console.error("API Client initialization error:", error.message);
    }
    return Promise.reject(error);
  }
);

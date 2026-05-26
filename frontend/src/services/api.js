import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  register: (data) => api.post("/api/auth/register", data),
  login: (data) => api.post("/api/auth/login", data),
  me: () => api.get("/api/auth/me"),
  permissions: () => api.get("/api/auth/me/permissions"),
  updateMe: (data) => api.patch("/api/auth/me", data),
  changePassword: (data) => api.post("/api/auth/change-password", data),
};

export const datasetsAPI = {
  list: (params) => api.get("/api/datasets/", { params }),
  get: (id) => api.get(`/api/datasets/${id}`),
  preview: (id) => api.get(`/api/datasets/${id}/preview`),
  upload: (formData) => api.post("/api/datasets/upload", formData, { headers: { "Content-Type": "multipart/form-data" } }),
  delete: (id) => api.delete(`/api/datasets/${id}`),
};

export const forecastsAPI = {
  list: (params) => api.get("/api/forecasts/", { params }),
  get: (id) => api.get(`/api/forecasts/${id}`),
  create: (data) => api.post("/api/forecasts/", data),
  delete: (id) => api.delete(`/api/forecasts/${id}`),
  getModels: () => api.get("/api/forecasts/models"),
  compare: (params) => api.post("/api/forecasts/compare", null, { params }),
  retrain: (id) => api.post(`/api/forecasts/${id}/retrain`),
};

export const dashboardAPI = {
  stats: (params) => api.get("/api/dashboard/stats", { params }),
  activity: (params) => api.get("/api/dashboard/activity", { params }),
  realtime: () => api.get("/api/dashboard/realtime"),
};

export const reportsAPI = {
  downloadExcel: (id) => api.get(`/api/reports/${id}/excel`, { responseType: "blob" }),
  downloadPDF: (id) => api.get(`/api/reports/${id}/pdf`, { responseType: "blob" }),
  getInsights: (id) => api.get(`/api/reports/${id}/insights`),
};

export const notificationsAPI = {
  list: (params) => api.get("/api/notifications/", { params }),
  unreadCount: () => api.get("/api/notifications/unread-count"),
  markRead: (id) => api.patch(`/api/notifications/${id}/read`),
  markAllRead: () => api.patch("/api/notifications/mark-all-read"),
  delete: (id) => api.delete(`/api/notifications/${id}`),
};

export const adminAPI = {
  stats: () => api.get("/api/admin/stats"),
  users: (params) => api.get("/api/admin/users", { params }),
  toggleActive: (id) => api.patch(`/api/admin/users/${id}/toggle-active`),
  toggleAdmin: (id) => api.patch(`/api/admin/users/${id}/toggle-admin`),
  updateRole: (id, role) => api.patch(`/api/admin/users/${id}/role`, null, { params: { role } }),
  deleteUser: (id) => api.delete(`/api/admin/users/${id}`),
  getRoles: () => api.get("/api/admin/roles"),
  datasets: (params) => api.get("/api/admin/datasets", { params }),
  forecasts: (params) => api.get("/api/admin/forecasts", { params }),
};

export const analyticsAPI = {
  regionWise: (params) => api.get("/api/analytics/region-wise", { params }),
  categoryWise: (params) => api.get("/api/analytics/category-wise", { params }),
  revenuePrediction: (params) => api.get("/api/analytics/revenue-prediction", { params }),
  inventoryRisk: (params) => api.get("/api/analytics/inventory-risk", { params }),
  globalSearch: (q) => api.get("/api/analytics/global-search", { params: { q } }),
};

export const monitoringAPI = {
  activityLogs: (params) => api.get("/api/monitoring/activity-logs", { params }),
  userActivity: (userId, params) => api.get(`/api/monitoring/user-activity/${userId}`, { params }),
  performance: (params) => api.get("/api/monitoring/performance", { params }),
  forecastHistory: (params) => api.get("/api/monitoring/forecast-history", { params }),
};

export const anomalyAPI = {
  detect: (data) => api.post("/api/anomalies/detect", data),
  list: () => api.get("/api/anomalies/"),
  get: (id) => api.get(`/api/anomalies/${id}`),
};

export default api;

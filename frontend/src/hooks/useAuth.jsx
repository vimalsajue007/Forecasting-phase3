import { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("user")); } catch { return null; }
  });
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      Promise.all([authAPI.me(), authAPI.permissions()])
        .then(([userRes, permRes]) => {
          setUser(userRes.data);
          setPermissions(permRes.data.permissions || []);
          localStorage.setItem("user", JSON.stringify(userRes.data));
        })
        .catch(() => {
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials) => {
    const res = await authAPI.login(credentials);
    const { access_token, user: userData } = res.data;
    localStorage.setItem("token", access_token);
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
    // Fetch permissions
    try {
      const permRes = await authAPI.permissions();
      setPermissions(permRes.data.permissions || []);
    } catch {}
    return userData;
  };

  const register = async (data) => {
    const res = await authAPI.register(data);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setPermissions([]);
  };

  const hasPermission = (permission) => permissions.includes(permission);
  const hasRole = (role) => {
    if (user?.is_admin) return true;
    const roleOrder = { super_admin: 3, analyst: 2, viewer: 1 };
    const userLevel = roleOrder[user?.role] || 1;
    const reqLevel = roleOrder[role] || 1;
    return userLevel >= reqLevel;
  };

  return (
    <AuthContext.Provider value={{ user, loading, permissions, login, register, logout, hasPermission, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};

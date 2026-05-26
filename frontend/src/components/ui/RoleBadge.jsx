export default function RoleBadge({ role }) {
  const config = {
    super_admin: { label: "Super Admin", className: "bg-purple-100 text-purple-700" },
    analyst: { label: "Analyst", className: "badge-info" },
    viewer: { label: "Viewer", className: "bg-gray-100 text-gray-600" },
  };
  const { label, className } = config[role] || config["viewer"];
  return <span className={`badge ${className}`}>{label}</span>;
}

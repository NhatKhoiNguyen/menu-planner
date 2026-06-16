import React, { useContext } from "react";
import { Navigate } from "react-router-dom";
import { UserContext } from "~/contexts/UserContext";

function PrivateRoute({ children, roles }) {
  const { user, loading } = useContext(UserContext);

  if (loading) return <div>Đang kiểm tra đăng nhập...</div>;

  if (!user) {
    return <Navigate to="/" replace />;
  }

  const unauthorized = !user || (roles && !roles.includes(user.role));

  if (unauthorized) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default PrivateRoute;

import React, { useState } from "react";
import "../../styles/AdminDashboard.css";
import UserManagement from "../../components/UserManagement";
import MealManagement from "../../components/MealManagement";
import MealApproval from "../../components/MealApproval";
import Statistics from "../../components/Statistics";

function AdminDashboard() {
  const [selectedTab, setSelectedTab] = useState("users");

  const renderContent = () => {
    switch (selectedTab) {
      case "users":
        return <UserManagement />;
      case "meals":
        return <MealManagement />;
      case "contributions":
        return <MealApproval />;
      case "statistics":
        return <Statistics />;
      default:
        return null;
    }
  };

  return (
    <div className="admin-dashboard">
      <aside className="sidebar">
        <h3>Trang quản trị</h3>
        <ul>
          <li
            className={selectedTab === "users" ? "active" : ""}
            onClick={() => setSelectedTab("users")}
          >
            Quản lý người dùng
          </li>
          <li
            className={selectedTab === "meals" ? "active" : ""}
            onClick={() => setSelectedTab("meals")}
          >
            Quản lý món ăn
          </li>
          <li
            className={selectedTab === "contributions" ? "active" : ""}
            onClick={() => setSelectedTab("contributions")}
          >
            Duyệt đóng góp món ăn
          </li>
          <li
            className={selectedTab === "statistics" ? "active" : ""}
            onClick={() => setSelectedTab("statistics")}
          >
            Thống kê
          </li>
        </ul>
      </aside>

      <main className="content">{renderContent()}</main>
    </div>
  );
}

export default AdminDashboard;

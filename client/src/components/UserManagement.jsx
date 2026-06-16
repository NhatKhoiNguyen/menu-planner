import React, { useEffect, useState } from "react";
import {
  Table,
  Button,
  Form,
  InputGroup,
  Pagination,
} from "react-bootstrap";
import EditUserModal from "./EditUserModal";
import "~/styles/MealManagement.css";

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedUser, setSelectedUser] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [notification, setNotification] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const usersPerPage = 10;

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/api/admin/users`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        const nonAdminUsers = data.users.filter(
          (u) => !u.is_admin && u.role !== "admin"
        );
        setUsers(nonAdminUsers);
        setFilteredUsers(nonAdminUsers);
      });
  }, []);

  useEffect(() => {
    const keyword = search.toLowerCase();
    const results = users.filter(
      (u) =>
        u.username.toLowerCase().includes(keyword) ||
        u._id.toLowerCase().includes(keyword)
    );
    setFilteredUsers(results);
    setCurrentPage(1);
  }, [search, users]);

  const handleDelete = async (id) => {
    if (!window.confirm("Xóa tài khoản này?")) return;
    await fetch(`${process.env.REACT_APP_API_URL}/api/admin/users/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });
    setUsers(users.filter((u) => u._id !== id));
  };

  const handleEditClick = (user) => {
    setSelectedUser(user);
    setShowEditModal(true);
  };

  // Pagination logic
  const indexOfLast = currentPage * usersPerPage;
  const indexOfFirst = indexOfLast - usersPerPage;
  const currentUsers = filteredUsers.slice(indexOfFirst, indexOfLast);
  const totalPages = Math.ceil(filteredUsers.length / usersPerPage);

  return (
    <div>
      <h3>Quản lý tài khoản</h3>
      <InputGroup className="mb-3 mt-3">
        <Form.Control
          placeholder="Tìm theo tên hoặc ID"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </InputGroup>
      {notification && (
        <div className="alert alert-success mt-3">{notification}</div>
      )}
      <div className="table-container">
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>ID</th>
              <th>Tên</th>
              <th>Email</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {currentUsers.map((user) => (
              <tr key={user._id}>
                <td>{user._id}</td>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>
                  <Button
                    size="sm"
                    variant="warning"
                    onClick={() => handleEditClick(user)}
                  >
                    Sửa
                  </Button>{" "}
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => handleDelete(user._id)}
                  >
                    Xóa
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>

      <Pagination className="justify-content-center">
        {[...Array(totalPages).keys()].map((n) => (
          <Pagination.Item
            key={n + 1}
            active={n + 1 === currentPage}
            onClick={() => setCurrentPage(n + 1)}
          >
            {n + 1}
          </Pagination.Item>
        ))}
      </Pagination>

      {selectedUser && (
        <EditUserModal
          show={showEditModal}
          handleClose={() => setShowEditModal(false)}
          user={selectedUser}
          onSave={(updated) => {
            setUsers(users.map((u) => (u._id === updated._id ? updated : u)));
            setNotification("Cập nhật tài khoản thành công!");
            setTimeout(() => setNotification(""), 3000);
            setShowEditModal(false);
          }}
        />
      )}
    </div>
  );
}

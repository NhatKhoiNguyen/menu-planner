import React, { useState, useEffect } from "react";
import { Modal, Button, Form } from "react-bootstrap";

export default function EditUserModal({ show, handleClose, user, onSave }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    if (user) {
      setUsername(user.username || "");
      setEmail(user.email || "");
    }
  }, [user]);

  const handleSave = async () => {
    const updatedUser = {
      _id: user._id,
      username,
    };

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${process.env.REACT_APP_API_URL}/api/admin/users/${user._id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updatedUser),
      });

      if (res.ok) {
        const updatedData = await res.json();
        onSave(updatedData.updated_user);
      } else {
        const data = await res.json();
        alert(data.error || "Cập nhật thất bại");
      }
    } catch (err) {
      console.error(err);
      alert("Lỗi máy chủ khi cập nhật");
    }
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Chỉnh sửa tài khoản</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group>
            <Form.Label>Tên người dùng</Form.Label>
            <Form.Control
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </Form.Group>
          <Form.Group className="mt-2">
            <Form.Label>Email</Form.Label>
            <Form.Control type="email" value={email} readOnly />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Hủy
        </Button>
        <Button variant="primary" onClick={handleSave}>
          Lưu
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

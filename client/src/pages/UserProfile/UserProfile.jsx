import React, { useContext, useState, useEffect } from "react";
import { Container, Form, Button, Alert } from "react-bootstrap";
import { UserContext } from "~/contexts/UserContext";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function UserProfile() {
  const { user, updateUser } = useContext(UserContext);
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!user && !token) {
      setTimeout(() => {
        navigate("/");
      }, 3000);
    }
  }, [user, token, navigate]);

  useEffect(() => {
    if (user) {
      setName(user.username);
    }
  }, [user]);

  if (!user && !token) {
    return (
      <Container className="py-4">
        <Alert
          variant="warning"
          style={{
            backgroundColor: "#fff3cd",
            borderColor: "#ffa500",
            color: "#856404",
          }}
        >
          <h5 style={{ color: "#FFA500" }}>
            Vui lòng đăng nhập để sử dụng chức năng.
          </h5>
          <p>Bạn sẽ được chuyển hướng về trang chủ trong giây lát...</p>
        </Alert>
      </Container>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");

    if (password && password !== confirmPassword) {
      setError("Mật khẩu xác nhận không khớp.");
      return;
    }

    try {
      const res = await axios.put(
        `${process.env.REACT_APP_API_URL}/api/users/${user._id}`,
        {
          username: name,
          password: password || undefined,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      localStorage.setItem("user", JSON.stringify(res.data));
      updateUser(res.data);
      setMessage("Cập nhật thành công!");
      setPassword("");
      setConfirmPassword("");
    } catch (err) {
      console.error(err);
      setError("Cập nhật thất bại.");
    }
  };

  return (
    <Container style={{ maxWidth: "500px", marginTop: "40px" }}>
      <h3>Hồ sơ người dùng</h3>
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Email (không thể thay đổi)</Form.Label>
          <Form.Control type="email" value={user?.email || ""} disabled />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Tên người dùng</Form.Label>
          <Form.Control
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Mật khẩu mới</Form.Label>
          <Form.Control
            type="password"
            value={password}
            placeholder="Để trống nếu không đổi"
            onChange={(e) => setPassword(e.target.value)}
          />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Xác nhận mật khẩu</Form.Label>
          <Form.Control
            type="password"
            value={confirmPassword}
            placeholder="Nhập lại mật khẩu mới"
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </Form.Group>

        <Button variant="primary" type="submit">
          Cập nhật
        </Button>

        {message && (
          <Alert variant="success" className="mt-3">
            {message}
          </Alert>
        )}
        {error && (
          <Alert variant="danger" className="mt-3">
            {error}
          </Alert>
        )}
      </Form>
    </Container>
  );
}

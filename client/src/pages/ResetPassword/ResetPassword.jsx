import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Container, Form, Button, Alert } from "react-bootstrap";

export default function ResetPassword() {
  const { token } = useParams(); // lấy token từ URL
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleReset = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Mật khẩu không khớp.");
      return;
    }

    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/reset-password/${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      const data = await res.json();
      if (res.ok) {
        setMessage("Mật khẩu đã được cập nhật. Đang chuyển hướng đến trang đăng nhập...");
        setError("");
        setTimeout(() => navigate("/"), 3000); // quay về trang chính hoặc đăng nhập
      } else {
        setError(data.message || "Có lỗi xảy ra.");
      }
    } catch (err) {
      setError("Lỗi máy chủ.");
    }
  };

  return (
    <Container className="mt-5" style={{ maxWidth: "500px" }}>
      <h3>Đặt lại mật khẩu</h3>
      <Form onSubmit={handleReset}>
        <Form.Group className="mt-3">
          <Form.Label>Mật khẩu mới</Form.Label>
          <Form.Control
            type="password"
            value={password}
            placeholder="Nhập mật khẩu mới"
            onChange={(e) => setPassword(e.target.value)}
          />
        </Form.Group>

        <Form.Group className="mt-3">
          <Form.Label>Nhập lại mật khẩu</Form.Label>
          <Form.Control
            type="password"
            value={confirmPassword}
            placeholder="Xác nhận mật khẩu mới"
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </Form.Group>

        {message && <Alert variant="success" className="mt-3">{message}</Alert>}
        {error && <Alert variant="danger" className="mt-3">{error}</Alert>}

        <Button variant="primary" type="submit" className="mt-4">Đặt lại mật khẩu</Button>
      </Form>
    </Container>
  );
}

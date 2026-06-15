import React, { useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import "~/styles/ModalLogin.css"
import "~/styles/ForgotPasswordModal.css"


export default function ForgotPasswordModal({ show, handleClose }) {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSendResetLink = async () => {
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();
      if (res.ok) {
        setMessage("Đường dẫn đặt lại mật khẩu đã được gửi đến email của bạn.");
        setError("");
      } else {
        setError(data.message || "Đã xảy ra lỗi.");
        setMessage("");
      }
    } catch (err) {
      setError("Lỗi máy chủ.");
      setMessage("");
    }
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton className="forgot-modal-header">
        <Modal.Title className="forgot-modal-title">Quên mật khẩu</Modal.Title>
      </Modal.Header>
      <Modal.Body className="forgot-modal-body">
        <Form>
          <Form.Group className="login-form-group">
            <Form.Label className="login-form-label">Email của bạn</Form.Label>
            <Form.Control
              type="email"
              placeholder="Nhập email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="login-form-control"
            />
          </Form.Group>
          {message && <p className="text-success mt-2">{message}</p>}
          {error && <p className="text-danger mt-2">{error}</p>}
        </Form>
      </Modal.Body>
      <Modal.Footer className="login-modal-footer">
        <Button variant="secondary" onClick={handleClose}>Đóng</Button>
        <Button variant="primary" onClick={handleSendResetLink}>Gửi liên kết</Button>
      </Modal.Footer>
    </Modal>
  );
}

import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { Modal, Button, Form } from "react-bootstrap";
import ModalRegister from "./ModalRegister";
import ForgotPasswordModal from "./ForgotPasswordModal";
import { UserContext } from "~/contexts/UserContext";
import "~/styles/ModalLogin.css";

export default function ModalLogin({ show, handleClose, onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [showForgotModal, setShowForgotModal] = useState(false);

  const { setUser } = useContext(UserContext);

  const navigate = useNavigate();

  const validateFields = () => {
    const newErrors = {};
    if (!email.trim()) newErrors.email = "Vui lòng nhập email";
    if (!password.trim()) newErrors.password = "Vui lòng nhập mật khẩu";
    return newErrors;
  };

  const handleLogin = async () => {
    const validationErrors = validateFields();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();

      if (res.status === 404) {
        setErrors((prev) => ({ ...prev, email: data.error }));
        return;
      }
      if (res.status === 401) {
        setErrors((prev) => ({ ...prev, password: data.error }));
        return;
      }

      if (res.ok) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("user", JSON.stringify(data.user));
        setUser({ ...data.user, role: data.user.is_admin ? "admin" : "user" });
        if (data.user.is_admin) {
          navigate("/admin");
        } else if (onLoginSuccess) {
          onLoginSuccess(data.user);
        }
        handleClose();
      } else {
        setErrors({ general: data.error || "Đăng nhập thất bại" });
      }
    } catch (err) {
      console.error(err);
      alert("Lỗi máy chủ");
    }
  };

  const handleRegisterRedirect = () => {
    setShowRegisterModal(true); // Mở modal đăng ký
    handleClose(); // Đóng modal đăng nhập
  };

  return (
    <>
      <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton className="login-modal-header">
          <Modal.Title className="login-modal-title">Đăng nhập</Modal.Title>
        </Modal.Header>
        <Modal.Body className="login-modal-body">
          <Form>
            <Form.Group className="login-form-group">
              <Form.Label className="login-form-label">Email</Form.Label>
              <Form.Control
                type="email"
                value={email}
                isInvalid={!!errors.email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setErrors((prev) => ({ ...prev, email: "", general: "" }));
                }}
                className="login-form-control"
              />
              <Form.Control.Feedback type="invalid">
                {errors.email}
              </Form.Control.Feedback>
            </Form.Group>
            <Form.Group className="login-form-group">
              <Form.Label className="login-form-label">Mật khẩu</Form.Label>
              <Form.Control
                type="password"
                value={password}
                isInvalid={!!errors.password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setErrors((prev) => ({ ...prev, password: "", general: "" }));
                }}
                className="login-form-control"
              />
              <Form.Control.Feedback type="invalid">
                {errors.password}
              </Form.Control.Feedback>
            </Form.Group>
          </Form>
          <div className="login-modal-link">
            <Button variant="link" onClick={() => setShowForgotModal(true)}>
              Quên mật khẩu?
            </Button>
          </div>
          <div className="login-modal-link mt-3">
            <span>Chưa có tài khoản? </span>
            <Button variant="link" onClick={handleRegisterRedirect}>
              Đăng ký ngay
            </Button>
          </div>
        </Modal.Body>
        <Modal.Footer className="login-modal-footer">
          <Button variant="secondary" onClick={handleClose}>
            Đóng
          </Button>
          <Button variant="primary" onClick={handleLogin}>
            Đăng nhập
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Hiển thị ModalRegister nếu showRegisterModal là true */}
      {showRegisterModal && (
        <ModalRegister
          show={showRegisterModal}
          handleClose={() => setShowRegisterModal(false)}
        />
      )}
      {/* Hiển thị ForgotPasswordModal nếu showForgotModal là true */}
      {showForgotModal && (
        <ForgotPasswordModal
          show={showForgotModal}
          handleClose={() => setShowForgotModal(false)}
        />
      )}
    </>
  );
}

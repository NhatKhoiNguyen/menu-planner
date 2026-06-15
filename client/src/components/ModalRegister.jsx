import React, { useState, useContext } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import { UserContext } from "~/contexts/UserContext";
import "~/styles/ModalRegister.css";

export default function ModalRegister({ show, handleClose }) {
  const [username, setUserName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState("");
  const { setUser } = useContext(UserContext);

  const validateFields = () => {
    const newErrors = {};
    if (!username.trim()) newErrors.username = "Tên không được bỏ trống";
    if (!email.trim()) newErrors.email = "Email không được bỏ trống";
    if (!password.trim()) newErrors.password = "Mật khẩu không được bỏ trống";
    if (!confirmPassword.trim())
      newErrors.confirmPassword = "Nhập lại mật khẩu";
    else if (password !== confirmPassword)
      newErrors.confirmPassword = "Mật khẩu không khớp";
    return newErrors;
  };

  const handleRegister = async () => {
    const validationErrors = validateFields();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });
      const data = await res.json();

      if (res.status === 409) {
        setErrors((prev) => ({ ...prev, email: data.error }));
        return;
      }

      if (res.ok) {
        // Tự động đăng nhập sau khi đăng ký
        const loginRes = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        const loginData = await loginRes.json();

        if (loginRes.ok) {
          localStorage.setItem("token", loginData.token);
          localStorage.setItem("user", JSON.stringify(loginData.user));
          setUser(loginData.user);
          handleClose();
        } else {
          // alert("Đăng ký thành công nhưng đăng nhập thất bại");
        }
      } else {
        // alert(data.message || "Đăng ký thất bại");
      }
    } catch (err) {
      console.error(err);
      alert("Lỗi máy chủ");
    }
  };

  const handleInputChange = (field, value) => {
    switch (field) {
      case "username":
        setUserName(value);
        break;
      case "email":
        setEmail(value);
        break;
      case "password":
        setPassword(value);
        break;
      case "confirmPassword":
        setConfirmPassword(value);
        break;
      default:
        break;
    }

    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }

    if (
      field === "confirmPassword" &&
      errors.confirmPassword &&
      password === value
    ) {
      setErrors((prev) => ({ ...prev, confirmPassword: "" }));
    }
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton className="register-modal-header">
        <Modal.Title className="register-modal-title">Đăng ký</Modal.Title>
      </Modal.Header>
      <Modal.Body className="register-modal-body">
        <Form>
          <Form.Group className="register-form-group">
            <Form.Label className="register-form-label">Tên</Form.Label>
            <Form.Control
              type="text"
              value={username}
              isInvalid={!!errors.username}
              onChange={(e) => handleInputChange("username", e.target.value)}
              className="register-form-control"
            />
            <Form.Control.Feedback type="invalid">
              {errors.username}
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="register-form-group">
            <Form.Label className="register-form-label">Email</Form.Label>
            <Form.Control
              type="email"
              value={email}
              isInvalid={!!errors.email}
              onChange={(e) => handleInputChange("email", e.target.value)}
              className="register-form-control"
            />
            <Form.Control.Feedback type="invalid">
              {errors.email}
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="register-form-group">
            <Form.Label className="register-form-label">Mật khẩu</Form.Label>
            <Form.Control
              type="password"
              value={password}
              isInvalid={!!errors.password}
              onChange={(e) => handleInputChange("password", e.target.value)}
              className="register-form-control"
            />
            <Form.Control.Feedback type="invalid">
              {errors.password}
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="register-form-group">
            <Form.Label className="register-form-label">
              Nhập lại mật khẩu
            </Form.Label>
            <Form.Control
              type="password"
              value={confirmPassword}
              isInvalid={!!errors.confirmPassword}
              onChange={(e) =>
                handleInputChange("confirmPassword", e.target.value)
              }
              className="register-form-control"
            />
            <Form.Control.Feedback type="invalid">
              {errors.confirmPassword}
            </Form.Control.Feedback>
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer className="register-modal-footer">
        <Button variant="secondary" onClick={handleClose}>
          Đóng
        </Button>
        <Button variant="success" onClick={handleRegister}>
          Đăng ký
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

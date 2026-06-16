import React, { useState, useContext } from "react";
import {
  Button,
  Dropdown,
} from "react-bootstrap";
import { FaUserCircle } from "react-icons/fa";
import "~/styles/Header.css";
import ModalLogin from "./ModalLogin";
import ModalRegister from "./ModalRegister";
import { UserContext } from "../contexts/UserContext";
import { useNavigate, useLocation } from "react-router-dom";

export default function Header() {
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const { user, setUser } = useContext(UserContext);

  const navigate = useNavigate();
  const location = useLocation();

  // Đăng xuất
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    window.location.reload();
  };

  return (
    <header className="header-wrapper d-flex justify-content-between align-items-center px-4 py-2">
      <div
        className="d-flex align-items-center"
        onClick={() => navigate("/")}
        style={{ cursor: "pointer" }}
      >
        <img
          src="/logo.png"
          alt="Logo"
          style={{ height: "60px" }}
          onClick={() => navigate("/")}
        />
        <h1 className="mb-0 ms-3">MEAL PLANNER</h1>
      </div>

      <div className="header-right d-flex flex-wrap justify-content-end align-items-center">
        {user?.role !== "admin" && (
          <Button
            variant="outline-primary"
            className="me-2"
            onClick={() => navigate("/search")}
          >
            Tìm món ăn qua ảnh
          </Button>
        )}
        {/* <Button
          variant="outline-primary"
          className="me-2"
          onClick={() => navigate("/search")}
        >
          Tìm món ăn qua ảnh
        </Button> */}
        {user ? (
          <Dropdown align="end">
            <Dropdown.Toggle
              variant="outline-primary"
              className="d-flex align-items-center user-menu-toggle"
            >
              <FaUserCircle className="me-2" size={20} />
              {user.name || user.email}
            </Dropdown.Toggle>

            <Dropdown.Menu className="user-menu-dropdown">
              {user.role !== "admin" && location.pathname !== "/" && (
                <Dropdown.Item onClick={() => navigate("/")}>
                  Trang chủ
                </Dropdown.Item>
              )}
              {location.pathname !== "/profile" && (
                <Dropdown.Item onClick={() => navigate("/profile")}>
                  Hồ sơ
                </Dropdown.Item>
              )}
              {user.role !== "admin" && location.pathname !== "/favorites" && (
                <Dropdown.Item onClick={() => navigate("/favorites")}>
                  Món ăn yêu thích
                </Dropdown.Item>
              )}
              {user.role !== "admin" && location.pathname !== "/history" && (
                <Dropdown.Item onClick={() => navigate("/history")}>
                  Lịch sử thực đơn
                </Dropdown.Item>
              )}
              {user.role !== "admin" &&
                location.pathname !== "/contribution" && (
                  <Dropdown.Item onClick={() => navigate("/contribution")}>
                    Đóng góp món ăn
                  </Dropdown.Item>
                )}
              {user.role === "admin" && location.pathname !== "/admin" && (
                <Dropdown.Item onClick={() => navigate("/admin")}>
                  Quản lý
                </Dropdown.Item>
              )}
              <Dropdown.Divider />
              <Dropdown.Item className="logout-item" onClick={handleLogout}>
                Đăng xuất
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        ) : (
          <>
            <Button
              variant="outline-primary"
              className="me-2"
              onClick={() => setShowLogin(true)}
            >
              Đăng nhập
            </Button>
            <Button
              variant="outline-success"
              onClick={() => setShowRegister(true)}
            >
              Đăng ký
            </Button>
          </>
        )}
      </div>

      <ModalLogin show={showLogin} handleClose={() => setShowLogin(false)} />

      <ModalRegister
        show={showRegister}
        handleClose={() => setShowRegister(false)}
      />
    </header>

    // <Navbar
    //   bg="warning"
    //   expand="lg"
    //   sticky="top"
    //   className="px-4 py-2 shadow-sm"
    // >
    //   <Container fluid className="px-0">
    //     <Navbar.Brand
    //       onClick={() => navigate("/")}
    //       style={{ cursor: "pointer" }}
    //     >
    //       <img src="/logo.png" alt="Logo" height="50" className="me-2" />
    //       <span className="fw-bold text-white">MEAL PLANNER</span>
    //     </Navbar.Brand>

    //     <Navbar.Toggle aria-controls="responsive-navbar-nav" />

    //     <Navbar.Collapse id="responsive-navbar-nav">
    //       <Nav className="ms-auto d-flex align-items-center flex-wrap gap-2">
    //         <Button
    //           variant="outline-light"
    //           onClick={() => navigate("/search")}
    //           className="me-2"
    //         >
    //           Tìm món ăn qua ảnh
    //         </Button>

    //         {user ? (
    //           <NavDropdown
    //             title={
    //               <span className="d-flex align-items-center">
    //                 <FaUserCircle className="me-2" /> {user.name || user.email}
    //               </span>
    //             }
    //             id="user-dropdown"
    //             align="end"
    //             className="text-white"
    //           >
    //             <NavDropdown.Item onClick={() => navigate("/profile")}>
    //               Hồ sơ
    //             </NavDropdown.Item>
    //             <NavDropdown.Item onClick={() => navigate("/favorites")}>
    //               Món yêu thích
    //             </NavDropdown.Item>
    //             <NavDropdown.Item onClick={() => navigate("/history")}>
    //               Lịch sử thực đơn
    //             </NavDropdown.Item>
    //             <NavDropdown.Divider />
    //             <NavDropdown.Item onClick={handleLogout}>
    //               Đăng xuất
    //             </NavDropdown.Item>
    //           </NavDropdown>
    //         ) : (
    //           <>
    //             <Button
    //               variant="outline-light"
    //               onClick={() => setShowLogin(true)}
    //               className="me-2"
    //             >
    //               Đăng nhập
    //             </Button>
    //             <Button variant="outline-light" onClick={() => setShowRegister(true)}>
    //               Đăng ký
    //             </Button>
    //           </>
    //         )}
    //       </Nav>
    //     </Navbar.Collapse>
    //   </Container>

    //   <ModalLogin show={showLogin} handleClose={() => setShowLogin(false)} />
    //   <ModalRegister
    //     show={showRegister}
    //     handleClose={() => setShowRegister(false)}
    //   />
    // </Navbar>
  );
}

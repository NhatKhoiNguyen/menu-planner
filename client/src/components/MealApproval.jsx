import React, { useEffect, useState } from "react";
import axios from "axios";
import { Container, Table, Button, Spinner, Modal } from "react-bootstrap";
import MealModal from "./MealModal";

const MealApproval = () => {
  const [pendingMeals, setPendingMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMeal, setSelectedMeal] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const token = localStorage.getItem("token");

  const fetchPendingMeals = async () => {
    try {
      const res = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/admin/pending-meals`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      console.log("Pending meals:", res.data);
      setPendingMeals(res.data);
    } catch (error) {
      console.error("Lỗi khi tải món chờ duyệt:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingMeals();
  }, []);

  const handleApprove = async (meal) => {
    const id = meal._id?.toString();
    try {
      await axios.post(
        `${process.env.REACT_APP_API_URL}/api/admin/approve-meal/${id}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setPendingMeals((prev) => prev.filter((meal) => meal._id !== id));
    } catch (error) {
      console.error("Duyệt món thất bại:", error);
    }
  };

  const handleReject = async (id) => {
    try {
      await axios.delete(`${process.env.REACT_APP_API_URL}/api/admin/reject-meal/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPendingMeals((prev) => prev.filter((meal) => meal._id !== id));
    } catch (error) {
      console.error("Từ chối món thất bại:", error);
    }
  };

  const handleEdit = (meal) => {
    console.log("Mở modal với meal:", meal);
    setSelectedMeal(meal);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setSelectedMeal(null);
    setShowModal(false);
  };

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" />
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <h3 className="mb-4">Danh sách món ăn chờ duyệt</h3>
      {pendingMeals.length === 0 ? (
        <p>Không có món ăn nào đang chờ duyệt.</p>
      ) : (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>ID</th>
              <th>Ngày đóng góp</th>
              <th>ID người đóng góp</th>
              <th>Người đóng góp</th>
              <th>Email</th>
              <th>Tên món ăn</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {pendingMeals.map((meal) => (
              <tr key={meal._id}>
                <td>{meal._id}</td>
                <td>
                  {meal.createdAt
                    ? new Date(meal.createdAt).toLocaleString("vi-VN", {
                        timeZone: "Asia/Ho_Chi_Minh",
                        hour12: false,
                      })
                    : "Không rõ"}
                </td>
                <td>{meal.submittedBy || "Không rõ"}</td>
                <td>{meal.contributorName || "Không rõ"}</td>
                <td>{meal.contributorEmail || "Không rõ"}</td>
                <td>{meal.title}</td>
                <td>
                  <Button
                    variant="warning"
                    size="sm"
                    className="me-1"
                    onClick={() => handleEdit(meal)}
                  >
                    Chỉnh sửa
                  </Button>
                  <Button
                    variant="success"
                    size="sm"
                    className="me-1"
                    onClick={() => handleApprove(meal)}
                  >
                    Duyệt
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleReject(meal._id)}
                  >
                    Từ chối
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      <MealModal
        show={showModal}
        onHide={handleCloseModal}
        meal={selectedMeal}
        onSave={() => {
          fetchPendingMeals();
          handleCloseModal();
        }}
      />
    </Container>
  );
};

export default MealApproval;

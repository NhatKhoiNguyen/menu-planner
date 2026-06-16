import React, { useEffect, useState } from "react";
import {
  Table,
  Button,
  InputGroup,
  Form,
  Pagination
} from "react-bootstrap";
import MealModal from "./MealModal";
import MealDetailModal from "./MealDetailModal";
import MealInstructionModal from "./MealInstructionModal";
import "~/styles/MealManagement.css";

export default function MealManagement() {
  const [meals, setMeals] = useState([]);
  const [search, setSearch] = useState("");
  const [filteredMeals, setFilteredMeals] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showInstructionModal, setShowInstructionModal] = useState(false);
  const [selectedMeal, setSelectedMeal] = useState(null);
  const [notification, setNotification] = useState("");
  const mealsPerPage = 30;

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/api/admin/meals`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setMeals(data.meals);
        setFilteredMeals(data.meals);
      });
  }, []);

  useEffect(() => {
    const keyword = search.toLowerCase();
    const results = meals.filter(
      (m) =>
        m.title.toLowerCase().includes(keyword) ||
        m._id.toLowerCase().includes(keyword)
    );
    setFilteredMeals(results);
    setCurrentPage(1);
  }, [search, meals]);

  const handleEditClick = (meal) => {
    console.log("Editing meal:", meal);
    setSelectedMeal(meal);
    setShowEditModal(true);
  };

  const handleAddClick = () => {
    setSelectedMeal(null);
    setShowAddModal(true);
  };

  const handleViewClick = (meal) => {
    setSelectedMeal(meal);
    setShowDetailModal(true);
  };

  const handleDelete = async (mealId) => {
    const confirm = window.confirm("Bạn có chắc muốn xóa món ăn này?");
    if (!confirm) return;

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(
        `${process.env.REACT_APP_API_URL}/api/admin/meals/${mealId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (res.ok) {
        setMeals(meals.filter((meal) => meal._id !== mealId));
        setNotification("Đã xóa món ăn thành công!");
        setTimeout(() => setNotification(""), 3000);
      } else {
        const data = await res.json();
        alert(data.error || "Không thể xóa món ăn.");
      }
    } catch (err) {
      console.error(err);
      alert("Lỗi máy chủ khi xóa món ăn.");
    }
  };

  const indexOfLast = currentPage * mealsPerPage;
  const indexOfFirst = indexOfLast - mealsPerPage;
  const currentMeals = filteredMeals.slice(indexOfFirst, indexOfLast);
  const totalPages = Math.ceil(filteredMeals.length / mealsPerPage);

  return (
    <div>
      <h3>Quản lý món ăn</h3>
      <InputGroup className="mb-3 mt-3">
        <Form.Control
          placeholder="Tìm theo tên hoặc ID"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Button variant="success" onClick={handleAddClick}>
          + Thêm món
        </Button>
      </InputGroup>
      {notification && (
        <div className="alert alert-success mt-3">{notification}</div>
      )}

      <div className="table-container">
        <Table striped bordered hover className="meal-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Tên món</th>
              <th>Calo (kcal)</th>
              <th>Chi phí</th>
              <th>Loại món</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {currentMeals.map((meal) => (
              <tr key={meal._id}>
                <td>{meal._id}</td>
                <td>{meal.title}</td>
                <td>{meal.energy}</td>
                <td>{meal.price?.toLocaleString()}đ</td>
                <td>{meal.type === "main" ? "Món chính" : "Món phụ"}</td>
                <td>
                  <Button
                    size="sm"
                    variant="info"
                    className="me-1"
                    onClick={() => handleViewClick(meal)}
                  >
                    Xem
                  </Button>
                  <Button
                    size="sm"
                    variant="warning"
                    className="me-1"
                    onClick={() => handleEditClick(meal)}
                  >
                    Sửa
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(meal._id)}
                  >
                    Xóa
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>

      <div className="pagination-container">
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
      </div>

      {showEditModal && (
        <MealModal
          show={showEditModal}
          onHide={() => setShowEditModal(false)}
          meal={selectedMeal}
          onSave={(updated) => {
            setMeals((prev) =>
              prev.map((m) => (m._id === updated._id ? updated : m))
            );
            setShowEditModal(false);
          }}
        />
      )}

      {showAddModal && (
        <MealModal
          show={showAddModal}
          onHide={() => setShowAddModal(false)}
          onSave={(added) => {
            setMeals((prev) => [added, ...prev]);
            setShowAddModal(false);
          }}
        />
      )}

      {showDetailModal && (
        <MealDetailModal
          show={showDetailModal}
          onHide={() => setShowDetailModal(false)}
          meal={selectedMeal}
          onShowInstructions={() => {
            setShowDetailModal(false);
            setShowInstructionModal(true);
          }}
          hideFavoriteButton={true}
        />
      )}

      {showInstructionModal && (
        <MealInstructionModal
          show={showInstructionModal}
          onHide={() => setShowInstructionModal(false)}
          meal={selectedMeal}
        />
      )}
    </div>
  );
}

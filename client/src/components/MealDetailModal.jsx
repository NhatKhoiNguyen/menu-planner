import React, { useState, useEffect } from "react";
import { Modal, Button } from "react-bootstrap";
import { toast } from "react-toastify";
import "../styles/MealDetailModal.css";
import axios from "axios";

const MealDetailModal = ({
  show,
  onHide,
  meal,
  onShowInstructions,
  hideFavoriteButton,
}) => {
  const [isFavorite, setIsFavorite] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);

  useEffect(() => {
    const checkIfFavorite = async () => {
      const token = localStorage.getItem("token");
      if (!token || !meal) {
        setIsFavorite(false);
        return;
      }

      try {
        const res = await axios.get(
          `${process.env.REACT_APP_API_URL}/api/favorites/list`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const exists = res.data.meals.some(
          (fav) => String(fav._id) === String(meal.id)
        );
        setIsFavorite(exists);
      } catch (err) {
        console.error("Lỗi kiểm tra món yêu thích:", err);
      }
    };

    if (show && meal) {
      // console.log("Meal passed to modal:", meal);
      checkIfFavorite();
    }
  }, [show, meal]);

  if (!meal) return null;

  const handleAddToFavorites = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      toast.warning("Vui lòng đăng nhập để lưu món yêu thích");
      setShowLoginModal(true);
      return;
    }

    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/favorites/add`,
        { meal_id: meal.id || meal._id},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (res.status === 200) {
        toast.success("Đã lưu vào món yêu thích!");
        setIsFavorite(true);
      }
    } catch (err) {
      console.error(err);
      toast.error("Không thể lưu món ăn!");
    }
  };

  return (
    <Modal show={show} onHide={onHide} centered className="meal-detail-modal">
      <Modal.Header closeButton>
        <Modal.Title>{meal.name || meal.title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <img
          src={meal.image || meal.main_image || "/placeholder.jpg"}
          alt={meal.name || meal.title}
          className="meal-image-modal"
        />
        <p>
          <strong>Calo:</strong>{" "}
          {meal.calories !== undefined
            ? `${meal.calories} kcal`
            : meal.energy !== undefined
            ? `${meal.energy} kcal`
            : "Không rõ"}
        </p>
        <p>
          <strong>Chi phí:</strong> {meal.price?.toLocaleString() || 0}₫
        </p>
        <p>
          <strong>Nguyên liệu:</strong>
        </p>
        <ul>
          {meal.ingredients?.map((ing, i) => (
            <li key={i}>
              {ing?.amount ?? ""} {ing?.name ?? ""}
            </li>
          ))}
        </ul>
        {meal.tags && (
          <p>
            <strong>Loại món:</strong>{" "}
            {meal.tags.map((tag, i) => (
              <span key={i} className="badge bg-info me-1">
                {tag}
              </span>
            ))}
          </p>
        )}
      </Modal.Body>
      <Modal.Footer className="d-flex justify-content-center flex-wrap gap-2">
        {!hideFavoriteButton && (
          <Button
            variant={isFavorite ? "success" : "primary"}
            className="px-3 fw-medium"
            onClick={handleAddToFavorites}
            disabled={isFavorite}
          >
            {isFavorite ? "Đã lưu" : "❤️ Lưu món yêu thích"}
          </Button>
        )}
        <Button
          variant="primary"
          className="px-3 fw-medium"
          onClick={onShowInstructions}
        >
          📖 Hướng dẫn nấu ăn
        </Button>
        <Button variant="secondary" className="px-3 fw-medium" onClick={onHide}>
          Đóng
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default MealDetailModal;

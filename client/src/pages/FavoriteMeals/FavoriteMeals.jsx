import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { Container, Spinner, Row, Col, Card, Button } from "react-bootstrap";
import "../../styles/FavoriteMeals.css";
import { toast } from "react-toastify";
import { UserContext } from "../../contexts/UserContext";
import MealDetailModal from "../../components/MealDetailModal";
import MealInstructionModal from "../../components/MealInstructionModal";
import { Alert } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

const FavoriteMeals = () => {
  const { user } = useContext(UserContext);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMeal, setSelectedMeal] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showInstructionModal, setShowInstructionModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

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
    const fetchFavorites = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;

        const res = await axios.get(
          `${process.env.REACT_APP_API_URL}/api/favorites/list`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (res.status === 200 && res.data.meals) {
          console.log(res.data.meals);
          setFavorites(res.data.meals);
        }
      } catch (error) {
        console.error("Lỗi khi tải món yêu thích:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchFavorites();
  }, []);

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

  const handleShowDetail = (meal) => {
    setSelectedMeal(meal);
    setShowDetailModal(true);
  };

  const handleCloseDetailModal = () => {
    setShowDetailModal(false);
    setSelectedMeal(null);
  };

  const handleShowInstructions = () => {
    setShowInstructionModal(true);
  };

  const handleCloseInstructions = () => {
    setShowInstructionModal(false);
  };

  const handleRemoveFavorite = async (mealId) => {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.delete(
        `${process.env.REACT_APP_API_URL}/api/favorites/remove/${mealId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (res.status === 200) {
        toast.success("Đã xóa khỏi danh sách yêu thích!");
        setFavorites(favorites.filter((meal) => meal._id !== mealId));
        console.log(mealId);
      }
    } catch (error) {
      console.error("Lỗi khi xóa món yêu thích:", error);
    }
  };

  const filteredFavorites = favorites.filter((meal) =>
    meal.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <Spinner animation="border" />;

  return (
    <div className="favorite-meals-container">
      <h4 className="text-center mb-4">Món ăn yêu thích</h4>
      <div className="input-group w-50 mx-auto mb-3">
        <input
          type="text"
          className="form-control"
          placeholder="Tìm món theo tên..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <span className="input-group-text">
          <i className="bi bi-search"></i>
        </span>
      </div>
      {filteredFavorites.length === 0 ? (
        <p className="text-center">Bạn chưa có món ăn yêu thích nào.</p>
      ) : (
        <Row xs={1} md={3} xl={5} className="g-4">
          {filteredFavorites.map((meal) => (
            <Col key={meal._id}>
              <Card
                className="meal-card h-100"
                onClick={() => handleShowDetail(meal)}
                style={{ cursor: "pointer", position: "relative" }}
              >
                <Card.Img
                  variant="top"
                  src={meal.main_image || "/placeholder.jpg"}
                  alt={meal.title}
                  className="meal-card-img"
                />
                <Card.Body className="d-flex flex-column">
                  <Card.Title>{meal.title}</Card.Title>
                  <Card.Text>
                    {meal.energy} kcal | {meal.price?.toLocaleString() || 0} ₫
                  </Card.Text>
                  <div className="mt-auto text-end">
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveFavorite(meal._id);
                      }}
                    >
                      Xóa
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {selectedMeal && (
        <>
          <MealDetailModal
            show={showDetailModal}
            onHide={handleCloseDetailModal}
            meal={selectedMeal}
            onShowInstructions={handleShowInstructions}
            hideFavoriteButton={true}
          />
          <MealInstructionModal
            show={showInstructionModal}
            onHide={handleCloseInstructions}
            meal={selectedMeal}
          />
        </>
      )}
    </div>
  );
};

export default FavoriteMeals;

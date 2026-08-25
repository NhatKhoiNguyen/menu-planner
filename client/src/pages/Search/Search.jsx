import React, { useState, useRef, useEffect } from "react";
import {
  Container,
  Button,
  Form,
  Spinner,
  Row,
  Col,
  Card,
} from "react-bootstrap";
import axios from "axios";
import MealDetailModal from "~/components/MealDetailModal";
import MealInstructionModal from "../../components/MealInstructionModal";
import "../../styles/Search.css";

export default function Search() {
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showInstructionModal, setShowInstructionModal] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [meals, setMeals] = useState([]);
  const [selectedMeal, setSelectedMeal] = useState(null);
  const [showCamera, setShowCamera] = useState(false);
  const [ingredients, setIngredients] = useState([]);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  let streamRef = useRef(null);

  useEffect(() => {
    const startCamera = async () => {
      if (!showCamera) return;

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: {
              ideal: "environment",
            },
            width: {
              ideal: 1280,
            },
            height: {
              ideal: 720,
            },
          },
          audio: false,
        });

        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Không thể mở camera sau:", err);

        // Fallback nếu camera sau không khả dụng
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false,
          });

          streamRef.current = stream;

          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        } catch (fallbackError) {
          console.error("Không thể mở camera:", fallbackError);
          alert("Không thể truy cập camera. Vui lòng kiểm tra quyền camera.");
          setShowCamera(false);
        }
      }
    };

    startCamera();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, [showCamera]);

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (!blob) return;

        const file = new File([blob], "captured.jpg", {
          type: "image/jpeg",
        });

        setSelectedImage(file);
        setPreviewUrl(URL.createObjectURL(blob));
        setShowCamera(false);
      },
      "image/jpeg",
      0.85,
    );
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSearch = async () => {
    if (!selectedImage) return;
    setLoading(true);
    setMeals([]);
    try {
      const formData = new FormData();
      formData.append("image", selectedImage);
      const res = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/search/image-search`,
        formData,
      );
      setMeals(res.data.meals || []);
      setIngredients(res.data.ingredients || []);
    } catch (err) {
      console.error("Lỗi tìm kiếm món ăn từ ảnh:", err);
    }
    setLoading(false);
  };
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

  return (
    <Container className="py-4">
      <h3 className="text-center mb-4">🔍 Tìm món ăn qua ảnh</h3>
      <Form>
        <Form.Group className="mb-3">
          <Form.Label>Chọn ảnh từ máy hoặc chụp</Form.Label>
          <Form.Control
            type="file"
            accept="image/*"
            onChange={handleImageChange}
          />
        </Form.Group>

        <Button
          variant="secondary"
          onClick={() => setShowCamera(!showCamera)}
          className="me-2"
        >
          {showCamera ? "Tắt camera" : "Chụp bằng camera"}
        </Button>

        {showCamera && (
          <div>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              width="320"
              height="240"
            />
            <canvas
              ref={canvasRef}
              style={{ display: "none" }}
            />
            <div className="my-2">
              <Button variant="success" onClick={capturePhoto}>
                📸 Chụp ảnh
              </Button>
            </div>
          </div>
        )}

        {/* {previewUrl && (
          <Row className="mt-3">
            <p>Ảnh đã chọn/chụp:</p>
            <Col md={6}>
              <img src={previewUrl} alt="Preview" className="img-fluid" />
            </Col>
            <Col md={6}>
              <h5>🧂 Nguyên liệu nhận diện:</h5>
              {ingredients.length > 0 && (
                <ul>
                  {ingredients.map((ing, idx) => (
                    <li key={idx}>{ing}</li>
                  ))}
                </ul>
              )}
            </Col>
          </Row>
        )} */}
        {previewUrl && (
          <div className="image-preview-wrapper">
            <div>
              <p>
                <strong>📷 Ảnh đã chọn hoặc chụp:</strong>
              </p>
              <img src={previewUrl} alt="Preview" className="image-preview" />
            </div>
            <div>
              <p>
                <strong>🍽️ Nguyên liệu nhận diện:</strong>
              </p>
              {ingredients.length > 0 ? (
                <ul className="ingredient-list">
                  {ingredients.map((ing, idx) => (
                    <li key={idx}>
                      {ing.charAt(0).toUpperCase() + ing.slice(1)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p>Chưa có nguyên liệu nào được nhận diện.</p>
              )}
            </div>
          </div>
        )}

        <div className="mt-3">
          <Button
            variant="primary"
            onClick={handleSearch}
            disabled={loading || !selectedImage}
            className="search-button"
          >
            {loading ? (
              <Spinner animation="border" size="sm" />
            ) : (
              "Gợi ý món ăn"
            )}
          </Button>
        </div>
      </Form>
      <Row xs={1} md={3} xl={5} className="g-4 mt-4">
        {meals.map((meal) => (
          <Col key={meal._id} md={4} className="mb-3">
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
                <div className="mt-auto text-end"></div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      
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
    </Container>
  );
}

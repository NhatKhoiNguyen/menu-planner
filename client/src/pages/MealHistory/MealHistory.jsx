import React, { useEffect, useState, useContext, useRef } from "react";
import axios from "axios";
import {
  Container,
  Card,
  ListGroup,
  Spinner,
  Row,
  Col,
  Form,
  Button,
} from "react-bootstrap";
import DatePicker, { registerLocale } from "react-datepicker";
import vi from "date-fns/locale/vi";
import "react-datepicker/dist/react-datepicker.css";
import { UserContext } from "../../contexts/UserContext";
import "../../styles/MealHistory.css";
import MealDetailModal from "../../components/MealDetailModal";
import MealInstructionModal from "../../components/MealInstructionModal";
import { Alert } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

registerLocale("vi", vi);

const MealHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useContext(UserContext);
  const [selectedMeal, setSelectedMeal] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showInstructionModal, setShowInstructionModal] = useState(false);
  const [fromDate, setFromDate] = useState(null);
  const [toDate, setToDate] = useState(null);

  const navigate = useNavigate();

  const token = localStorage.getItem("token");

  const scrollRefs = useRef([]);
  scrollRefs.current = [];

  const scrollByOffset = (index, offset) => {
    const ref = scrollRefs.current[index];
    if (ref) {
      ref.scrollBy({ left: offset, behavior: "smooth" });
    }
  };

  const openMealDetail = (meal) => {
    setSelectedMeal(meal);
    setShowDetailModal(true);
  };

  const closeMealDetail = () => {
    setSelectedMeal(null);
    setShowDetailModal(false);
  };

  const filteredHistory = history.filter((item) => {
    const itemDate = new Date(item.date);
    const from = fromDate ? new Date(fromDate) : null;
    const to = toDate ? new Date(toDate) : null;

    if (to) {
      to.setHours(23, 59, 59, 999);
    }

    const afterFrom = !from || itemDate >= from;
    const beforeTo = !to || itemDate <= to;

    return afterFrom && beforeTo;
  });

  useEffect(() => {
    if (!user && !token) {
      setTimeout(() => {
        navigate("/");
      }, 3000);
    }
  }, [user, token, navigate]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem("token");
        console.log("Token:", token);
        if (!token) return;

        const res = await axios.get(
          `${process.env.REACT_APP_API_URL}/api/meals_history/list`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (res.status === 200) {
          console.log("Dữ liệu lịch sử:", res.data);
          setHistory(res.data);
        }
      } catch (err) {
        console.error("Lỗi khi tải lịch sử thực đơn:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
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

  if (loading) return <Spinner animation="border" />;

  return (
    <div className="meal-history-container">
      <h4 className="text-center mb-4">Lịch sử thực đơn</h4>
      <Form className="date-filter-form">
        <Form.Label>Lọc theo khoảng ngày (dd/mm/yyyy):</Form.Label>
        <div className="d-flex flex-wrap align-items-center gap-2 mt-2">
          <DatePicker
            selected={fromDate ? new Date(fromDate) : null}
            onChange={(date) => setFromDate(date)}
            dateFormat="dd/MM/yyyy"
            locale="vi"
            placeholderText="Từ ngày"
          />
          <span>đến</span>
          <DatePicker
            selected={toDate ? new Date(toDate) : null}
            onChange={(date) => setToDate(date)}
            dateFormat="dd/MM/yyyy"
            locale="vi"
            placeholderText="Đến ngày"
          />
          <Button
            variant="outline-secondary"
            onClick={() => {
              setFromDate(null);
              setToDate(null);
            }}
          >
            Xóa lọc
          </Button>
        </div>
      </Form>
      {filteredHistory.length === 0 ? (
        <p className="text-center">Không có thực đơn nào.</p>
      ) : (
        filteredHistory.map((item, index) => (
          <Card className="mb-4 meal-history-card" key={item._id}>
            <Card.Header>
              <strong>Ngày:</strong>{" "}
              {new Date(item.date).toLocaleDateString("vi-VN")}
            </Card.Header>
            <div className="position-relative">
              <button
                className="scroll-button left"
                onClick={() => scrollByOffset(index, -300)}
              >
                &#8249;
              </button>
              <Card.Body>
                <div
                  className="daily-plan-scroll-container mb-3"
                  ref={(el) => (scrollRefs.current[index] = el)}
                >
                  <div className="scroll-wrapper">
                    {item.plan.map((dailyPlan, idx) => {
                      let totalCalories = 0;
                      let totalPrice = 0;

                      Object.values(dailyPlan).forEach(({ main, snack }) => {
                        if (main) {
                          totalCalories += main.calories || 0;
                          totalPrice += main.price || 0;
                        }
                        if (snack) {
                          totalCalories += snack.calories || 0;
                          totalPrice += snack.price || 0;
                        }
                      });

                      return (
                        <div key={idx} className="daily-plan-card mb-3">
                          <h6 className="mb-2">Thực đơn ngày {idx + 1}</h6>
                          <p className="text-muted mb-2">
                            Tổng calo: {totalCalories} kcal | Tổng chi phí:{" "}
                            {totalPrice.toLocaleString()}₫
                          </p>
                          <ListGroup variant="flush">
                            {Object.entries(dailyPlan).map(
                              ([mealType, data], i) => (
                                <ListGroup.Item
                                  key={`${idx}-${i}`}
                                  className="meal-entry"
                                >
                                  <strong>{mealType}</strong>
                                  <Row>
                                    {data.main && (
                                      <Col xs={12} md={6} className="meal-item">
                                        <div
                                          onClick={() =>
                                            openMealDetail(data.main)
                                          }
                                          style={{ cursor: "pointer" }}
                                        >
                                          <img
                                            src={
                                              data.main.image ||
                                              "/placeholder.jpg"
                                            }
                                            alt={data.main.name}
                                            className="meal-image"
                                          />
                                          <div className="meal-text">
                                            🍽️ {data.main.name}
                                            <br />
                                            {data.main.calories} kcal |{" "}
                                            {data.main.price?.toLocaleString() ||
                                              0}
                                            ₫
                                          </div>
                                        </div>
                                      </Col>
                                    )}
                                    {data.snack && (
                                      <Col xs={12} md={6} className="meal-item">
                                        <div
                                          onClick={() =>
                                            openMealDetail(data.snack)
                                          }
                                          style={{ cursor: "pointer" }}
                                        >
                                          <img
                                            src={
                                              data.snack.image ||
                                              "/placeholder.jpg"
                                            }
                                            alt={data.snack.name}
                                            className="meal-image"
                                          />
                                          <div className="meal-text">
                                            🥤 {data.snack.name}
                                            <br />
                                            {data.snack.calories} kcal |{" "}
                                            {data.snack.price?.toLocaleString() ||
                                              0}
                                            ₫
                                          </div>
                                        </div>
                                      </Col>
                                    )}
                                  </Row>
                                </ListGroup.Item>
                              )
                            )}
                          </ListGroup>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </Card.Body>
              <button
                className="scroll-button right"
                onClick={() => scrollByOffset(index, 300)}
              >
                &#8250;
              </button>
            </div>
          </Card>
        ))
      )}

      <MealDetailModal
        show={showDetailModal}
        onHide={closeMealDetail}
        meal={selectedMeal}
        onShowInstructions={() => {
          setShowDetailModal(false);
          setShowInstructionModal(true);
        }}
      />

      <MealInstructionModal
        show={showInstructionModal}
        onHide={() => setShowInstructionModal(false)}
        meal={selectedMeal}
      />
    </div>
  );
};

export default MealHistory;

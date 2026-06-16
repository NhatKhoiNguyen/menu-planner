import React, { useState, useContext } from "react";
import { Form, Button, Row, Col } from "react-bootstrap";
import "~/styles/MealInputForm.css";
import CalorieSuggestionModal from "./CalorieSuggestionModal";
import MealSuggestionResult from "./MealSuggestionResult";
import { UserContext } from "../contexts/UserContext";

export default function MealInputForm() {
  const { user } = useContext(UserContext);
  const [budget, setBudget] = useState("");
  const [budgetType, setBudgetType] = useState("daily");
  const [calories, setCalories] = useState("");
  const [preferences, setPreferences] = useState({});
  const [showModal, setShowModal] = useState(false);
  const [numDays, setNumDays] = useState(3);
  const [mainMeals] = useState(["Sáng", "Trưa", "Tối"]);
  const [allergens, setAllergens] = useState([]);
  const [finalSuggestionData, setFinalSuggestionData] = useState(null);
  const [allowFallback, setAllowFallback] = useState(false);
  const [userInput, setUserInput] = useState(null);

  const isLoggedIn = !!user;
  
  const token = localStorage.getItem("token");

  const checkboxOptions = [
    "Món Á",
    "Món Âu",
    "Kết hợp Á - Âu",
    "Món chay",
    "Ít dầu mỡ",
    "Tránh dị ứng",
    "Không gluten",
    "Không lactose",
  ];

  const allergenOptions = [
    "Trứng",
    "Hải sản",
    "Sữa",
    "Đậu phộng",
    "Đậu nành",
    "Lúa mì",
  ];

  const handleCheckboxChange = (label) => {
    setPreferences((prev) => ({ ...prev, [label]: !prev[label] }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!budget || !calories) {
      alert("Vui lòng nhập đầy đủ Ngân sách và Lượng calo mỗi ngày.");
      return;
    }

    const selectedPrefs = Object.keys(preferences).filter(
      (key) => preferences[key] && key !== "Tránh dị ứng"
    );

    const requestData = {
      budget: parseInt(budget),
      constraint_type: budgetType === "total" ? "total" : "daily",
      calories: parseInt(calories), // calories per day
      preferences: selectedPrefs,
      allergens,
      numDays,
      mainMeals,
      allowFallback,
      isLoggedIn,
    };

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/meals/suggest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const error = await response.json();
        alert("Lỗi gợi ý: " + error.error);
        return;
      }

      const suggestionPlan = await response.json();

      setFinalSuggestionData(suggestionPlan); // bạn sẽ dùng dữ liệu này để render thực đơn
      setUserInput(requestData);
    } catch (err) {
      console.error("Lỗi kết nối tới backend:", err);
      alert("Đã xảy ra lỗi khi kết nối tới server.");
    }

    // const suggestionPlan = generateMealPlan(finalInput);
    // setFinalSuggestionData(suggestionPlan);
    // setUserInput(finalInput);
  };

  return (
    <div className="meal-form-wrapper">
      <Form onSubmit={handleSubmit}>
        <Row className="mb-3">
          <Col md={6}>
            <Form.Group controlId="budget">
              <Form.Label>Ngân sách (VNĐ)</Form.Label>
              <Form.Control
                type="number"
                placeholder="Nhập số tiền"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
              />
              <div className="mt-2">
                <Form.Check
                  type="radio"
                  inline
                  label="Giới hạn mỗi ngày"
                  name="budgetType"
                  checked={budgetType === "daily"}
                  onChange={() => setBudgetType("daily")}
                />
                <Form.Check
                  type="radio"
                  inline
                  label="Giới hạn cho tổng số ngày"
                  name="budgetType"
                  checked={budgetType === "total"}
                  onChange={() => setBudgetType("total")}
                />
              </div>
            </Form.Group>
          </Col>

          <Col md={6}>
            <Form.Group controlId="calories">
              <Form.Label>Lượng calo mỗi ngày</Form.Label>
              <Form.Control
                type="number"
                placeholder="Ví dụ: 2000"
                value={calories}
                onChange={(e) => setCalories(e.target.value)}
              />
              <p
                className="calorie-suggestion-link"
                onClick={() => setShowModal(true)}
              >
                🔍 Gợi ý lượng calo nếu bạn không biết
              </p>
            </Form.Group>
          </Col>
        </Row>

        <Row className="mb-3">
          <Col>
            <Form.Label>Lựa chọn thực đơn</Form.Label>
            <div className="d-flex flex-wrap gap-3">
              {checkboxOptions.map((label) => (
                <Form.Check
                  key={label}
                  type="checkbox"
                  label={label}
                  checked={!!preferences[label]}
                  onChange={() => handleCheckboxChange(label)}
                />
              ))}
            </div>
          </Col>
        </Row>

        {preferences["Tránh dị ứng"] && (
          <div className="mt-3 ms-3">
            <Form.Label>Thành phần cần tránh:</Form.Label>
            <div className="d-flex flex-wrap gap-3">
              {allergenOptions.map((item) => (
                <Form.Check
                  key={item}
                  type="checkbox"
                  label={item}
                  checked={allergens.includes(item)}
                  onChange={() =>
                    setAllergens((prev) =>
                      prev.includes(item)
                        ? prev.filter((a) => a !== item)
                        : [...prev, item]
                    )
                  }
                />
              ))}
            </div>
          </div>
        )}

        <Row className="mb-3">
          <Col md={6}>
            <Form.Group>
              <Form.Label>Số ngày gợi ý (1-7)</Form.Label>
              <Form.Control
                type="number"
                min={1}
                max={7}
                value={numDays}
                onChange={(e) => setNumDays(parseInt(e.target.value))}
              />
            </Form.Group>
          </Col>
          {/* <Col md={6}>
            <Form.Label>Thêm tùy chọn</Form.Label>
            <Form.Check
              type="checkbox"
              label="Cho phép chọn món rẻ nhất nếu không tìm được món phù hợp"
              checked={allowFallback}
              onChange={(e) => setAllowFallback(e.target.checked)}
            />
          </Col> */}
        </Row>

        <div className="text-center mt-4">
          <Button type="submit">Gợi ý thực đơn</Button>
        </div>
      </Form>

      {finalSuggestionData && (
        <MealSuggestionResult
          suggestionPlan={finalSuggestionData}
          userInput={userInput}
          preferences={Object.keys(preferences).filter(
            (key) => preferences[key] && key !== "Tránh dị ứng"
          )}
          allergens={allergens}
        />
      )}

      <CalorieSuggestionModal
        show={showModal}
        handleClose={() => setShowModal(false)}
        setSuggestedCalories={(value) => setCalories(value)}
      />
    </div>
  );
}

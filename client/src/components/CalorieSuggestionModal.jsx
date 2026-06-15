import React, { useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import "~/styles/CalorieSuggestionModal.css";

export default function CalorieSuggestionModal({
  show,
  handleClose,
  setSuggestedCalories,
}) {
  const [formData, setFormData] = useState({
    age: "",
    weight: "",
    height: "",
    gender: "male",
    activity: "moderate",
    goal: "maintain",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const calculateCalories = () => {
    const { age, weight, height, gender, activity, goal } = formData;
    const w = parseFloat(weight);
    const h = parseFloat(height);
    const a = parseInt(age);

    if (!w || !h || !a) return;

    let bmr =
      gender === "male"
        ? 10 * w + 6.25 * h - 5 * a + 5
        : 10 * w + 6.25 * h - 5 * a - 161;

    const activityFactors = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      very_active: 1.9,
    };

    const goals = {
      lose: 0.8,
      maintain: 1,
      gain: 1.15,
    };

    const tdee = bmr * activityFactors[activity];
    const finalCalories = tdee * goals[goal];

    setSuggestedCalories(Math.round(finalCalories));
    handleClose();
  };

  return (
    <Modal show={show} onHide={handleClose} centered className="calorie-modal">
      <Modal.Header closeButton>
        <Modal.Title>Gợi ý lượng calo cần thiết</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form className="modal-form">
          <Form.Group className="mb-2">
            <Form.Label>Tuổi</Form.Label>
            <Form.Control
              name="age"
              type="number"
              value={formData.age}
              onChange={handleChange}
            />
          </Form.Group>
          <Form.Group className="mb-2">
            <Form.Label>Cân nặng (kg)</Form.Label>
            <Form.Control
              name="weight"
              type="number"
              value={formData.weight}
              onChange={handleChange}
            />
          </Form.Group>
          <Form.Group className="mb-2">
            <Form.Label>Chiều cao (cm)</Form.Label>
            <Form.Control
              name="height"
              type="number"
              value={formData.height}
              onChange={handleChange}
            />
          </Form.Group>
          <Form.Group className="mb-2">
            <Form.Label>Giới tính</Form.Label>
            <Form.Select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
            >
              <option value="male">Nam</option>
              <option value="female">Nữ</option>
            </Form.Select>
          </Form.Group>
          <Form.Group className="mb-2">
            <Form.Label>Mức độ vận động</Form.Label>
            <Form.Select
              name="activity"
              value={formData.activity}
              onChange={handleChange}
            >
              <option value="sedentary">Ít vận động (ngồi nhiều)</option>
              <option value="light">
                Vận động nhẹ (tập thể dục 1-3 ngày/tuần)
              </option>
              <option value="moderate">
                Vận động vừa (tập thể dục 3-5 ngày/tuần)
              </option>
              <option value="active">
                Vận động nhiều (tập thể dục 6-7 ngày/tuần)
              </option>
              <option value="very_active">
                Vận động rất nhiều (công việc thể chất cao hoặc tập luyện hai
                lần/ngày)
              </option>
            </Form.Select>
          </Form.Group>
          <Form.Group className="mb-2">
            <Form.Label>Mục tiêu</Form.Label>
            <Form.Select
              name="goal"
              value={formData.goal}
              onChange={handleChange}
            >
              <option value="lose">Giảm cân</option>
              <option value="maintain">Duy trì cân nặng</option>
              <option value="gain">Tăng cân</option>
            </Form.Select>
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Đóng
        </Button>
        <Button variant="primary" onClick={calculateCalories}>
          Tính calo
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

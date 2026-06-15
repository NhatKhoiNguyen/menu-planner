import React, { useState, useEffect } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import "~/styles/MealModal.css";
import axios from "axios";

const CLOUDINARY_UPLOAD_PRESET = "Meal Planner";
const CLOUDINARY_CLOUD_NAME = "dbkrr1ezd";

export default function MealModal({ show, onHide, meal, onSave }) {
  const [title, setTitle] = useState(meal?.title || "");
  const [energy, setEnergy] = useState(meal?.energy || 0);
  const [price, setPrice] = useState(meal?.price || 0);
  const [type, setType] = useState(meal?.type || "main");
  const [servings, setServings] = useState(meal?.servings || 1);
  const [tags, setTags] = useState(meal?.tags || []);
  const [mainImage, setMainImage] = useState(meal?.main_image || "");
  const [ingredients, setIngredients] = useState(meal?.ingredients || []);
  const [steps, setSteps] = useState(meal?.steps || [{ step: "", images: [] }]);
  const [allergens, setAllergens] = useState(meal?.allergens || []);
  const [uploading, setUploading] = useState(false);

  const availableTags = [
    "Món Á",
    "Món Âu",
    "Kết hợp Á - Âu",
    "Món chay",
    "Ít dầu mỡ",
    "Không gluten",
    "Không lactose",
  ];

  useEffect(() => {
    if (meal) {
      setTitle(meal.title || "");
      setEnergy(meal.energy || 0);
      setPrice(meal.price || 0);
      setType(meal.type || "main");
      setServings(meal.servings || 1);
      setTags(meal.tags || []);
      setMainImage(meal.main_image || "");
      setIngredients(meal.ingredients || []);
      setSteps(meal.steps || [{ step: "", images: [] }]);
      setAllergens(meal.allergens || []);
    }
  }, [meal]);

  const uploadToCloudinary = async (file) => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("upload_preset", CLOUDINARY_UPLOAD_PRESET);

      const res = await fetch(
        `https://api.cloudinary.com/v1_1/${CLOUDINARY_CLOUD_NAME}/image/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();
      if (!data.secure_url) throw new Error("Upload failed");
      return data.secure_url;
    } catch (err) {
      console.error("Upload error:", err);
      alert("Lỗi khi tải ảnh lên Cloudinary");
      return null;
    } finally {
      setUploading(false);
    }
  };

  const handleAddIngredient = () => {
    setIngredients([...ingredients, { name: "", amount: "" }]);
  };

  const handleRemoveIngredient = (index) => {
    const updated = [...ingredients];
    updated.splice(index, 1);
    setIngredients(updated);
  };

  const handleAddStep = () => {
    setSteps([...steps, { step: "", images: [] }]);
  };

  const handleRemoveStep = (index) => {
    const updated = [...steps];
    updated.splice(index, 1);
    setSteps(updated);
  };

  const handleAddImageToStep = async (stepIndex, fileOrUrl) => {
    const updatedSteps = [...steps];
    if (fileOrUrl instanceof File) {
      const uploadedUrl = await uploadToCloudinary(fileOrUrl);
      if (!uploadedUrl) return;
      updatedSteps[stepIndex].images.push(uploadedUrl);
    } else if (typeof fileOrUrl === "string") {
      const isValidUrl =
        fileOrUrl.startsWith("http://") || fileOrUrl.startsWith("https://");
      if (isValidUrl) {
        updatedSteps[stepIndex].images.push(fileOrUrl);
      } else {
        alert("URL ảnh không hợp lệ");
        return;
      }
    }
    setSteps(updatedSteps);
  };

  const handleRemoveImageFromStep = (stepIndex, imageIndex) => {
    const updatedSteps = [...steps];
    updatedSteps[stepIndex].images.splice(imageIndex, 1);
    setSteps(updatedSteps);
  };

  const handleAutoEnergy = async () => {
    if (!title || !ingredients || ingredients.length === 0) {
      alert("Vui lòng nhập nguyên liệu trước khi gợi ý calo.");
      return;
    }

    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/auto/energy`,
        {
          title,
          ingredients,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      if (res.data?.energy) {
        setEnergy(res.data.energy);
      } else {
        alert(res.data.error || "Không thể gợi ý calo.");
      }
    } catch (err) {
      console.error("Lỗi gợi ý calo:", err);
    }
  };

  const handleAutoPrice = async () => {
    if (!ingredients || ingredients.length === 0) {
      alert("Vui lòng nhập nguyên liệu trước khi gợi ý chi phí.");
      return;
    }

    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/auto/price`,
        {
          title,
          ingredients,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      if (res.data?.price) {
        setPrice(res.data.price);
      } else {
        alert(res.data.error || "Không thể gợi ý chi phí.");
      }
    } catch (err) {
      console.error("Lỗi gợi ý giá:", err);
    }
  };

  const handleAutoTags = async () => {
    if (!ingredients || ingredients.length === 0) {
      alert("Vui lòng nhập nguyên liệu trước khi gợi ý thể loại món.");
      return;
    }

    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/auto/tags`,
        {
          title,
          ingredients,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      if (res.data?.tags) {
        setTags(res.data.tags);
      } else {
        alert(res.data.error || "Không thể gợi ý thể loại món.");
      }
    } catch (err) {
      console.error("Lỗi gợi ý thể loại món:", err);
    }
  };

  const handleAutoAllergens = async () => {
    if (!ingredients || ingredients.length === 0) {
      alert("Vui lòng nhập nguyên liệu trước khi gợi ý dị ứng.");
      return;
    }

    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/auto/allergens`,
        {
          title,
          ingredients,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      if (Array.isArray(res.data?.allergens)) {
        setAllergens(res.data.allergens);

        if (res.data.allergens.length === 0) {
          alert("Không có thành phần dị ứng.");
        }
      } else {
        alert(res.data.error || "Không thể gợi ý dị ứng.");
      }
    } catch (err) {
      console.error(err);
      alert("Đã xảy ra lỗi khi gợi ý dị ứng.");
    }
  };

  const validateForm = () => {
    if (!title.trim()) {
      alert("Vui lòng nhập tên món ăn.");
      return false;
    }

    if (
      ingredients.length === 0 ||
      ingredients.some((i) => !i.name || !i.amount)
    ) {
      alert("Vui lòng nhập đầy đủ nguyên liệu và định lượng.");
      return false;
    }

    if (steps.length === 0 || steps.some((s) => !s.step.trim())) {
      alert("Vui lòng nhập đầy đủ các bước nấu ăn.");
      return false;
    }

    if (!tags || tags.length === 0) {
      alert("Vui lòng chọn ít nhất một thể loại món ăn (tag).");
      return false;
    }

    if (energy <= 0) {
      alert("Vui lòng nhập lượng calo hợp lệ.");
      return false;
    }

    if (price < 0) {
      alert("Giá món ăn không hợp lệ.");
      return false;
    }

    if (servings <= 0) {
      alert("Số khẩu phần phải lớn hơn 0.");
      return false;
    }

    return true;
  };

  const handleSubmit = async () => {
    console.log("Submit với meal:", meal);
    console.log("Meal source:", meal?.source);
    if (!validateForm()) return;
    
    const isPending = meal && meal.source === "pending";
    const method = meal ? "PUT" : "POST";
    const url = meal
      ? isPending
        ? `${process.env.REACT_APP_API_URL}/api/admin/pending-meals/${meal._id}`
        : `${process.env.REACT_APP_API_URL}/api/admin/meals/${meal._id}`
      : `${process.env.REACT_APP_API_URL}/api/admin/meals`;

    const payload = {
      title,
      energy,
      price,
      type,
      servings,
      allergens,
      main_image: mainImage,
      ingredients,
      steps,
      tags,
    };

    const res = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (res.ok) {
      onSave(data.meal);
    } else {
      alert(data.error || "Thất bại khi lưu món ăn");
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg" backdrop="static" className="custom-meal-modal">
      <Modal.Header closeButton>
        <Modal.Title>{meal ? "Chỉnh sửa" : "Thêm"} món ăn</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group>
            <Form.Label>Tên món</Form.Label>
            <Form.Control
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </Form.Group>

          <hr />
          <h5>Nguyên liệu</h5>
          {ingredients.map((ing, i) => (
            <div key={i} className="d-flex gap-2 mb-2">
              <Form.Control
                placeholder="Tên"
                value={ing.name}
                onChange={(e) => {
                  const updated = [...ingredients];
                  updated[i].name = e.target.value;
                  setIngredients(updated);
                }}
              />
              <Form.Control
                placeholder="Lượng"
                value={ing.amount}
                onChange={(e) => {
                  const updated = [...ingredients];
                  updated[i].amount = e.target.value;
                  setIngredients(updated);
                }}
              />
              <Button
                variant="danger"
                onClick={() => handleRemoveIngredient(i)}
              >
                X
              </Button>
            </div>
          ))}
          <Button variant="secondary" size="sm" onClick={handleAddIngredient}>
            + Thêm nguyên liệu
          </Button>
          {ingredients.length === 0 && (
            <div style={{ fontSize: "1rem", color: "red" }}>
              *Nhập nguyên liệu trước để dùng tính năng gợi ý
            </div>
          )}

          <hr />
          <Form.Label>Calo</Form.Label>
          <Form.Control
            type="number"
            value={energy}
            onChange={(e) => setEnergy(parseInt(e.target.value))}
            style={{ maxWidth: "120px" }}
          />
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={handleAutoEnergy}
          >
            Gợi ý calo
          </Button>

          <Form.Group className="mt-2">
            <Form.Label>Chi phí</Form.Label>
            <Form.Control
              type="number"
              value={price}
              onChange={(e) => setPrice(parseInt(e.target.value))}
              style={{ maxWidth: "120px" }}
            />
            <Button
              variant="outline-secondary"
              size="sm"
              className="ms-2"
              onClick={handleAutoPrice}
            >
              Gợi ý chi phí
            </Button>
          </Form.Group>

          <Form.Group className="mt-2">
            <Form.Label>Khẩu phần</Form.Label>
            <Form.Control
              type="number"
              value={servings}
              onChange={(e) => setServings(parseInt(e.target.value))}
              style={{ maxWidth: "120px" }}
            />
          </Form.Group>

          <Form.Group className="mt-2">
            <Form.Label>Thể loại món</Form.Label>
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={handleAutoTags}
            >
              Gợi ý thể loại món
            </Button>
            <div className="d-flex flex-wrap gap-2">
              {availableTags.map((tag) => (
                <Form.Check
                  key={tag}
                  type="checkbox"
                  label={tag}
                  checked={tags.includes(tag)}
                  onChange={() =>
                    setTags((prev) =>
                      prev.includes(tag)
                        ? prev.filter((t) => t !== tag)
                        : [...prev, tag]
                    )
                  }
                />
              ))}
            </div>
          </Form.Group>

          <Form.Group className="mt-2">
            <Form.Label>Loại món ăn</Form.Label>
            <Form.Select value={type} onChange={(e) => setType(e.target.value)}>
              <option value="main">Món chính</option>
              <option value="snack">Món phụ</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mt-2">
            <Form.Label>Tránh dị ứng</Form.Label>
            <Button
              variant="outline-secondary"
              size="sm"
              className="ms-2"
              onClick={handleAutoAllergens}
            >
              Gợi ý dị ứng
            </Button>
            <div className="d-flex flex-wrap gap-2 mt-2">
              {[
                "Trứng",
                "Hải sản",
                "Sữa",
                "Đậu phộng",
                "Đậu nành",
                "Lúa mì",
              ].map((allergen) => (
                <Form.Check
                  key={allergen}
                  type="checkbox"
                  label={allergen}
                  checked={allergens.includes(allergen)}
                  onChange={() =>
                    setAllergens((prev) =>
                      prev.includes(allergen)
                        ? prev.filter((a) => a !== allergen)
                        : [...prev, allergen]
                    )
                  }
                />
              ))}
            </div>
          </Form.Group>

          <Form.Group className="mt-2">
            <Form.Label>Ảnh món ăn</Form.Label>
            <Form.Control
              type="text"
              placeholder="Dán URL ảnh"
              value={mainImage}
              onChange={(e) => setMainImage(e.target.value)}
            />
            <Form.Control
              type="file"
              className="mt-1"
              accept="image/*"
              onChange={async (e) => {
                if (e.target.files[0]) {
                  const url = await uploadToCloudinary(e.target.files[0]);
                  if (url) setMainImage(url);
                }
              }}
            />
            {mainImage && (
              <img
                src={mainImage}
                alt="main dish"
                style={{ maxHeight: "120px", marginTop: "10px" }}
              />
            )}
          </Form.Group>

          <hr />
          <h5>Các bước thực hiện</h5>
          {steps.map((step, i) => (
            <div key={i} className="mb-3 border p-2 rounded">
              <Form.Label>Bước {i + 1}</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                placeholder="Mô tả bước"
                value={step.step}
                onChange={(e) => {
                  const updated = [...steps];
                  updated[i].step = e.target.value;
                  setSteps(updated);
                }}
              />
              <div className="mt-2">
                <Form.Label>Thêm ảnh</Form.Label>
                <Form.Control
                  type="file"
                  onChange={(e) => {
                    if (e.target.files[0])
                      handleAddImageToStep(i, e.target.files[0]);
                  }}
                />
                <Form.Control
                  className="mt-1"
                  type="text"
                  placeholder="Dán URL ảnh và nhấn Enter"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && e.target.value) {
                      handleAddImageToStep(i, e.target.value);
                      e.target.value = "";
                      e.preventDefault();
                    }
                  }}
                />
              </div>
              <div className="mt-2 d-flex flex-wrap gap-2">
                {step.images.map((img, idx) => (
                  <div key={idx} style={{ position: "relative" }}>
                    <img
                      src={img}
                      alt=""
                      style={{ height: "80px", borderRadius: 4 }}
                    />
                    <Button
                      variant="danger"
                      size="sm"
                      style={{
                        position: "absolute",
                        top: 0,
                        right: 0,
                        padding: "2px 6px",
                      }}
                      onClick={() => handleRemoveImageFromStep(i, idx)}
                    >
                      ×
                    </Button>
                  </div>
                ))}
              </div>
              <Button
                className="mt-2"
                variant="outline-danger"
                size="sm"
                onClick={() => handleRemoveStep(i)}
              >
                Xóa bước này
              </Button>
            </div>
          ))}
          <Button variant="secondary" size="sm" onClick={handleAddStep}>
            + Thêm bước
          </Button>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Hủy
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={uploading}>
          {uploading ? "Đang tải ảnh..." : "Lưu"}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

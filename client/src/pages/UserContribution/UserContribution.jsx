import React, { useContext, useState, useEffect } from "react";
import { Container, Form, Button, Row, Col, Image } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import "../../styles/UserContribution.css";
import { Alert } from "react-bootstrap";
import { UserContext } from "../../contexts/UserContext";
import axios from "axios";

const CLOUDINARY_UPLOAD_PRESET = "Meal Planner";
const CLOUDINARY_CLOUD_NAME = "dbkrr1ezd";

const availableTags = [
  "Món Á",
  "Món Âu",
  "Kết hợp Á - Âu",
  "Không gluten",
  "Không lactose",
  "Ít dầu mỡ",
  "Ăn kiêng",
];

const allergenOptions = [
  "Trứng",
  "Hải sản",
  "Sữa",
  "Đậu phộng",
  "Đậu nành",
  "Lúa mì",
];

const UserContribution = () => {
  const [title, setTitle] = useState("");
  const [ingredients, setIngredients] = useState([]);
  const [steps, setSteps] = useState([]);
  const [energy, setEnergy] = useState(0);
  const [price, setPrice] = useState(0);
  const [servings, setServings] = useState(1);
  const [tags, setTags] = useState([]);
  const [type, setType] = useState("main");
  const [allergens, setAllergens] = useState([]);
  const [mainImage, setMainImage] = useState("");
  const [uploading, setUploading] = useState(false);

  const navigate = useNavigate();

  const { user } = useContext(UserContext);
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!user && !token) {
      setTimeout(() => {
        navigate("/");
      }, 3000);
    }
  }, [user, token, navigate]);

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

  const handleAddIngredient = () =>
    setIngredients([...ingredients, { name: "", amount: "" }]);

  const handleRemoveIngredient = (index) =>
    setIngredients(ingredients.filter((_, i) => i !== index));

  const handleAddStep = () => setSteps([...steps, { step: "", images: [] }]);

  const handleRemoveStep = (index) =>
    setSteps(steps.filter((_, i) => i !== index));

  const handleAddImageToStep = async (index, fileOrUrl) => {
    let url =
      typeof fileOrUrl === "string"
        ? fileOrUrl
        : await uploadToCloudinary(fileOrUrl);
    if (!url) return;
    const updatedSteps = [...steps];
    updatedSteps[index].images.push(url);
    setSteps(updatedSteps);
  };

  const handleRemoveImageFromStep = (stepIndex, imgIndex) => {
    const updatedSteps = [...steps];
    updatedSteps[stepIndex].images.splice(imgIndex, 1);
    setSteps(updatedSteps);
  };

  const handleAutoEnergy = async () => {
    if (!ingredients || ingredients.length === 0) {
      alert("Vui lòng nhập nguyên liệu trước khi gợi ý calo.");
      return;
    }

    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/auto/energy`,
        {
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

  const handleSubmit = async () => {
    if (!title || ingredients.length === 0 || steps.length === 0) {
      alert("Vui lòng điền đầy đủ tên món, nguyên liệu và hướng dẫn.");
      return;
    }
    const data = {
      title,
      ingredients,
      steps,
      energy,
      price,
      servings,
      tags,
      type,
      allergens,
      main_image: mainImage,
    };
    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/users/contribute`,
        data,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (res.data.success) {
        alert("Gửi đóng góp thành công! Cảm ơn bạn.");
      } else {
        alert(res.data.message || "Gửi đóng góp thất bại.");
      }
    } catch (err) {
      console.error("Lỗi khi gửi đóng góp:", err);
      alert("Đã xảy ra lỗi khi gửi đóng góp.");
    }
  };

  return (
    <Container className="contribute-container py-4">
      <h3>Đóng góp món ăn</h3>
      <Form>
        <Form.Group className="mt-3">
          <Form.Label>Tên món</Form.Label>
          <Form.Control
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </Form.Group>

        <hr />
        <h5>Nguyên liệu</h5>
        {ingredients.map((ing, i) => (
          <Row key={i} className="mb-2">
            <Col>
              <Form.Control
                placeholder="Tên"
                value={ing.name}
                onChange={(e) => {
                  const updated = [...ingredients];
                  updated[i].name = e.target.value;
                  setIngredients(updated);
                }}
              />
            </Col>
            <Col>
              <Form.Control
                placeholder="Lượng"
                value={ing.amount}
                onChange={(e) => {
                  const updated = [...ingredients];
                  updated[i].amount = e.target.value;
                  setIngredients(updated);
                }}
              />
            </Col>
            <Col xs="auto">
              <Button
                variant="danger"
                onClick={() => handleRemoveIngredient(i)}
              >
                X
              </Button>
            </Col>
          </Row>
        ))}
        <Button size="sm" onClick={handleAddIngredient}>
          + Thêm nguyên liệu
        </Button>
        {ingredients.length === 0 && (
          <div style={{ fontSize: "1rem", color: "red" }}>
            *Nhập nguyên liệu trước để dùng tính năng gợi ý
          </div>
        )}

        <hr />
        <Form.Group>
          <Form.Label>Calo</Form.Label>
          <Form.Control
            type="number"
            value={energy}
            onChange={(e) => setEnergy(parseInt(e.target.value))}
            style={{ maxWidth: "150px" }}
          />
          <Button size="sm" onClick={handleAutoEnergy}>
            Gợi ý calo
          </Button>
        </Form.Group>

        <Form.Group className="mt-2">
          <Form.Label>Chi phí</Form.Label>
          <Form.Control
            type="number"
            value={price}
            onChange={(e) => setPrice(parseInt(e.target.value))}
            style={{ maxWidth: "150px" }}
          />
          <Button size="sm" className="ms-2" onClick={handleAutoPrice}>
            Gợi ý chi phí
          </Button>
        </Form.Group>

        <Form.Group className="mt-2">
          <Form.Label>Khẩu phần</Form.Label>
          <Form.Control
            type="number"
            value={servings}
            onChange={(e) => setServings(parseInt(e.target.value))}
            style={{ maxWidth: "150px" }}
          />
        </Form.Group>

        <Form.Group className="mt-3">
          <Form.Label>Thể loại món</Form.Label>
          <Button size="sm" onClick={handleAutoTags}>
            Gợi ý
          </Button>
          <div className="d-flex flex-wrap gap-2 mt-2">
            {availableTags.map((tag) => (
              <Form.Check
                inline
                key={tag}
                type="checkbox"
                label={tag}
                checked={tags.includes(tag)}
                onChange={() =>
                  setTags(
                    tags.includes(tag)
                      ? tags.filter((t) => t !== tag)
                      : [...tags, tag]
                  )
                }
              />
            ))}
          </div>
        </Form.Group>

        <Form.Group className="mt-3">
          <Form.Label>Loại món ăn</Form.Label>
          <Form.Select
            value={type}
            onChange={(e) => setType(e.target.value)}
            style={{ maxWidth: "200px" }}
          >
            <option value="main">Món chính</option>
            <option value="snack">Món phụ</option>
          </Form.Select>
        </Form.Group>

        <Form.Group className="mt-3">
          <Form.Label>Tránh dị ứng</Form.Label>
          <Button size="sm" onClick={handleAutoAllergens} className="ms-2">
            Gợi ý
          </Button>
          <div className="d-flex flex-wrap gap-2 mt-2">
            {allergenOptions.map((a) => (
              <Form.Check
                key={a}
                inline
                type="checkbox"
                label={a}
                checked={allergens.includes(a)}
                onChange={() =>
                  setAllergens(
                    allergens.includes(a)
                      ? allergens.filter((al) => al !== a)
                      : [...allergens, a]
                  )
                }
              />
            ))}
          </div>
        </Form.Group>

        <Form.Group className="mt-3">
          <Form.Label>Ảnh món ăn</Form.Label>
          <Form.Control
            type="text"
            value={mainImage}
            placeholder="Dán URL ảnh"
            onChange={(e) => setMainImage(e.target.value)}
          />
          <Form.Control
            className="mt-1"
            type="file"
            accept="image/*"
            onChange={async (e) => {
              if (e.target.files[0]) {
                setUploading(true);
                const url = await uploadToCloudinary(e.target.files[0]);
                if (url) setMainImage(url);
                setUploading(false);
              }
            }}
          />
          {mainImage && <Image src={mainImage} height={120} className="mt-2" />}
        </Form.Group>

        <hr />
        <h5>Hướng dẫn nấu ăn</h5>
        {steps.map((step, i) => (
          <div key={i} className="step-card rounded p-3 mb-3">
            <Form.Label>Bước {i + 1}</Form.Label>
            <Form.Control
              as="textarea"
              rows={2}
              value={step.step}
              placeholder="Mô tả bước"
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
                type="text"
                placeholder="Dán URL ảnh và nhấn Enter"
                className="mt-1"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && e.target.value) {
                    handleAddImageToStep(i, e.target.value);
                    e.preventDefault();
                    e.target.value = "";
                  }
                }}
              />
              <div className="step-images d-flex flex-wrap gap-2 mt-2">
                {step.images.map((img, idx) => (
                  <div key={idx} style={{ position: "relative" }}>
                    <img
                      className="img-preview"
                      src={img}
                      height={80}
                      alt=""
                      style={{ borderRadius: 4 }}
                    />
                    <Button
                      size="sm"
                      variant="danger"
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
                variant="outline-danger"
                size="sm"
                className="mt-2"
                onClick={() => handleRemoveStep(i)}
              >
                Xóa bước này
              </Button>
            </div>
          </div>
        ))}
        <Button variant="primary" size="sm" onClick={handleAddStep}>
          + Thêm bước
        </Button>

        <hr />
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={uploading}
          className="mt-3"
        >
          {uploading ? "Đang tải ảnh..." : "Gửi đóng góp"}
        </Button>
      </Form>
    </Container>
  );
};

export default UserContribution;

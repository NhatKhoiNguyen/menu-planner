import React from "react";
import MealInputForm from '~/components/MealInputForm';
import '~/styles/Home.css';

export default function Home() {
  
  
  const handleFormSubmit = (data) => {
    console.log('Dữ liệu form:', data);
  };

  return (
    <div className="home-page">
      <div className="hero-banner">
        <div className="hero-text">
          <h2>Khám phá thực đơn phù hợp với bạn</h2>
          <p>Nhập thông tin để được gợi ý thực đơn theo ngân sách và nhu cầu calo mỗi ngày</p>
        </div>
      </div>

      <div className="container-fluid home-form-section">
        <MealInputForm onSubmit={handleFormSubmit} />
      </div>
    </div>
  );
}

import React from "react";
import { Modal, Button } from "react-bootstrap";
import '../styles/MealInstructionModal.css';

const MealInstructionModal = ({ show, onHide, meal }) => {
  if (!meal) return null;

  return (
    <Modal show={show} onHide={onHide} centered className="meal-instruction-modal">
      <Modal.Header closeButton>
        <Modal.Title>📖 Hướng dẫn nấu: {meal.name}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {meal.steps ? (
          <ol>
            {meal.steps.map((stepData, index) => (
              <li key={index} className="mb-3">
                <div>{stepData.step}</div>
                {stepData.images?.length > 0 && (
                  <div className="mb-2">
                    {stepData.images.map((img, imgIdx) => (
                      <img
                        key={imgIdx}
                        src={img}
                        alt={`Bước ${index + 1} hình ảnh ${imgIdx + 1}`}
                        style={{
                          width: "100%",
                          borderRadius: "8px",
                          marginBottom: "5px",
                          objectFit: "cover",
                        }}
                      />
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ol>
        ) : (
          <p className="text-muted">Không có hướng dẫn nấu ăn.</p>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Đóng
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default MealInstructionModal;

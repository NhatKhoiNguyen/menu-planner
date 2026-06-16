import React, { useState, useEffect, useRef, useContext } from "react";
import { Button } from "react-bootstrap";
import { CSSTransition } from "react-transition-group";
import "../styles/MealSuggestionResult.css";
import { UserContext } from "~/contexts/UserContext";
import ModalLogin from "./ModalLogin";
import MealDetailModal from "./MealDetailModal";
import MealInstructionModal from "./MealInstructionModal";
import axios from "axios";

const defaultMeals = ["Sáng", "Trưa", "Tối"];

const MealCard = React.forwardRef(
  (
    {
      meal,
      onToggleList,
      showOptions,
      options,
      onSelect,
      onClickDetail,
      calorieLimit,
      priceLimit,
      type,
    },
    ref
  ) => {
    const [searchMode, setSearchMode] = React.useState(false);
    const [searchInput, setSearchInput] = React.useState("");
    const [searchResults, setSearchResults] = React.useState([]);

    if (!meal) return null;
    const name = meal.name || meal.title;
    const image = meal.image || meal.main_image;
    const calories = meal.calories || meal.energy;

    const handleSearch = async () => {
      if (!searchInput.trim()) return;
      const params = new URLSearchParams({ q: searchInput.trim() });
      if (typeof calorieLimit === "number") {
        const calMin = Math.floor(calorieLimit * 0.8);  // cho phép lệch -20%
        const calMax = Math.ceil(calorieLimit * 1.1);
        params.append("min_cal", calMin);
        params.append("max_cal", calMax);
      }
      if (typeof priceLimit === "number") {
        params.append("max_price", priceLimit);
      }
      if (type) {
        params.append("type", type);
      }
      try {
        const res = await fetch(
          `${process.env.REACT_APP_API_URL}/api/meals/search?${params.toString()}`
        );
        const data = await res.json();
        setSearchResults(data);
      } catch (error) {
        console.error("Search error", error);
        setSearchResults([]);
      }
    };

    const resetSearch = () => {
      setSearchInput("");
      setSearchResults([]);
    };

    const toggleSearchMode = () => {
      setSearchMode(!searchMode);
      if (showOptions) onToggleList();
      if (searchMode) resetSearch();
    };

    return (
      <div
        ref={ref}
        className="meal-card shadow-sm p-2 rounded bg-white mb-2 position-relative"
        onClick={() => onClickDetail(meal)}
        style={{ cursor: "pointer" }}
      >
        {meal.image && (
          <img
            src={image}
            alt={name}
            className="img-fluid rounded mb-2"
            style={{ width: "100%", height: "150px", objectFit: "cover" }}
          />
        )}
        <div className="meal-text-wrapper">
          <p className="meal-name mb-1 fw-bold">{name}</p>
          <p className="meal-detail text-muted">
            {calories} kcal – {meal.price.toLocaleString()}₫
          </p>
        </div>

        <div className="d-flex gap-2 justify-content-between button-wrapper">
          <button
            className="btn btn-sm btn-outline-primary fixed-btn flex-fill"
            onClick={(e) => {
              e.stopPropagation(); // Ngăn mở modal khi click vào nút
              if (searchMode) return;
              onToggleList();
            }}
            disabled={searchMode}
          >
            {showOptions ? "Đóng" : "Món gợi ý"}
          </button>

          <button
            className="btn btn-sm btn-outline-primary fixed-btn flex-fill"
            onClick={(e) => {
              e.stopPropagation();
              toggleSearchMode();
            }}
            disabled={showOptions}
          >
            {searchMode ? "Đóng" : "Tìm món khác"}
          </button>
        </div>

        {showOptions && (
          <div
            className="meal-options mt-2"
            onClick={(e) => e.stopPropagation()}
            style={{
              overflowX: "auto",
              whiteSpace: "nowrap",
              paddingBottom: "0.5rem",
            }}
          >
            {options.length === 0 ? (
              <p className="text-muted">Không có món tương tự</p>
            ) : (
              options.map((option, index) => {
                const optionName = option.name || option.title;
                const optionImage = option.image || option.main_image;
                const optionCalories = option.calories || option.energy;

                return (
                  <div
                    key={index}
                    className="option-card d-inline-block bg-white rounded shadow-sm border me-2 p-2"
                    style={{
                      width: "140px",
                      verticalAlign: "top",
                      cursor: "pointer",
                    }}
                    onClick={() => onClickDetail(option)}
                  >
                    {optionImage && (
                      <img
                        src={optionImage}
                        alt={optionName}
                        className="img-fluid rounded mb-2"
                        style={{
                          width: "100%",
                          height: "80px",
                          objectFit: "cover",
                        }}
                      />
                    )}
                    <div
                      className="fw-semibold text-truncate"
                      title={optionName}
                    >
                      {optionName}
                    </div>
                    <div className="text-muted small mb-1">
                      {optionCalories} kcal – {option.price?.toLocaleString()}₫
                    </div>
                    <button
                      className="btn btn-sm btn-outline-success w-100"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelect(option);
                      }}
                    >
                      Đổi
                    </button>
                  </div>
                );
              })
            )}
          </div>
        )}

        {searchMode && (
          <div
            className="manual-search mt-2"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="input-group input-group-sm mb-2">
              <input
                type="text"
                className="form-control"
                placeholder="Nhập tên món ăn"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
              />
              <button
                className="btn btn-outline-secondary"
                type="button"
                onClick={handleSearch}
              >
                🔍
              </button>
            </div>

            <div
              className="meal-options"
              style={{
                overflowX: "auto",
                whiteSpace: "nowrap",
                paddingBottom: "0.5rem",
              }}
            >
              {searchResults.length === 0 ? (
                <p className="text-muted">
                  Không có món nào phù hợp với từ khóa và giới hạn
                </p>
              ) : (
                searchResults.map((result, index) => (
                  <div
                    key={index}
                    className="option-card d-inline-block bg-white rounded shadow-sm border me-2 p-2"
                    style={{
                      width: "140px",
                      verticalAlign: "top",
                      cursor: "pointer",
                    }}
                    onClick={() => onClickDetail(result)}
                  >
                    {result.image && (
                      <img
                        src={result.image}
                        alt={result.name}
                        className="img-fluid rounded mb-2"
                        style={{
                          width: "100%",
                          height: "80px",
                          objectFit: "cover",
                        }}
                      />
                    )}
                    <div
                      className="fw-semibold text-truncate"
                      title={result.name}
                    >
                      {result.name}
                    </div>
                    <div className="text-muted small mb-1">
                      {result.calories} kcal – {result.price?.toLocaleString()}₫
                    </div>
                    <button
                      className="btn btn-sm btn-outline-success w-100"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelect(result);
                      }}
                    >
                      Đổi
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    );
  }
);



const MealSuggestionResult = ({
  suggestionPlan = null,
  userInput = {},
  preferences,
  allergens,
}) => {
  const { user } = useContext(UserContext);
  const { calories, budget } = userInput;
  const [mealPlan, setMealPlan] = useState([]);
  const [dailySnacks, setDailySnacks] = useState([]);
  const [showOptions, setShowOptions] = useState({}); // track which card is showing options
  const [mealOptions, setMealOptions] = useState({});
  const [selectedMeal, setSelectedMeal] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showInstructionModal, setShowInstructionModal] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);


  const openMealDetail = (meal) => {
    setSelectedMeal(meal);
    setShowDetailModal(true);
  };



  const handleLoginSuccess = (user) => {
    setShowLoginModal(false);
    window.location.reload();
  };

  const snackRefs = useRef({});

  const toggleSnack = async (dayIndex, mealType) => {
    const newSnacks = [...dailySnacks];
    const snackVisible = !newSnacks[dayIndex][mealType];
    newSnacks[dayIndex][mealType] = snackVisible;

    const meal = mealPlan[dayIndex][mealType];
    const mainMeal = meal.main;
    const previousSnack = meal.snack;

    const original_calories =
      meal.original_calories ??
      mainMeal.calories + (previousSnack?.calories || 0);
    const original_cost =
      meal.original_cost ?? mainMeal.price + (previousSnack?.price || 0);

    const currentMain = {
      ...mainMeal,
      original_calories,
      original_cost,
    };
    try {
      let updatedSnack = null;

      if (snackVisible) {
        // Mở snack: chỉ gọi toggle-snack để lấy snack phù hợp
        const res = await fetch(
          `${process.env.REACT_APP_API_URL}/api/meals/toggle-snack`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ currentMain, preferences, allergens }),
          }
        );
        const data = await res.json();
        console.log("Snack toggle response:", data);
        updatedSnack = data.adjustedSnack;
        console.log("Updated snack:", updatedSnack);
      }

      const newPlan = [...mealPlan];
      newPlan[dayIndex] = { ...newPlan[dayIndex] };
      newPlan[dayIndex][mealType] = {
        ...newPlan[dayIndex][mealType],
        main: currentMain,
        snack: snackVisible ? updatedSnack : null,
        original_calories,
        original_cost,
      };

      setMealPlan(newPlan);
      setDailySnacks(newSnacks);
    } catch (error) {
      console.error("Lỗi toggleSnack:", error);
    }
  };

  // useEffect(() => {
  //   let plan = [];
  //   let snacks = [];

  //   if (suggestionPlan && suggestionPlan.length > 0) {
  //     plan = suggestionPlan;
  //     snacks = suggestionPlan.map((dayMeals) => {
  //       const snackVisible = {};
  //       Object.keys(dayMeals).forEach((mealType) => {
  //         snackVisible[mealType] = false;
  //       });
  //       return snackVisible;
  //     });
  //   } else {
  //     for (let i = 0; i < numDays; i++) {
  //       const day = {};
  //       const snackVisible = {};
  //       defaultMeals.forEach((mealType) => {
  //         day[mealType] = {
  //           main: getRandomMeal("main"),
  //           snack: getRandomMeal("snack"),
  //         };
  //         snackVisible[mealType] = false;
  //       });
  //       plan.push(day);
  //       snacks.push(snackVisible);
  //     }
  //   }

  //   setMealPlan(plan);
  //   setDailySnacks(snacks);
  // }, [suggestionPlan]);

  useEffect(() => {
    console.log("suggestionPlan:", suggestionPlan);
    if (suggestionPlan && suggestionPlan.length > 0) {
      const snacks = suggestionPlan.map((dayMeals) => {
        const snackVisible = {};
        Object.keys(dayMeals).forEach((mealType) => {
          snackVisible[mealType] = true;
        });
        return snackVisible;
      });

      const mealRatios = { Sáng: 0.2, Trưa: 0.4, Tối: 0.4 };

      // let totalCaloriesUsed = 0;
      // let totalCostUsed = 0;

      // for (const dayMeals of suggestionPlan) {
      //   for (const mealType of Object.keys(dayMeals)) {
      //     const main = dayMeals[mealType]?.main;
      //     const snack = dayMeals[mealType]?.snack;
      //     totalCaloriesUsed += (main?.calories ?? 0) + (snack?.calories ?? 0);
      //     totalCostUsed += (main?.price ?? 0) + (snack?.price ?? 0);
      //   }
      // }

      const updatedPlan = suggestionPlan.map((dayMeals) => {
        const updatedDayMeals = { ...dayMeals };
        for (const mealType of Object.keys(updatedDayMeals)) {
          const ratio = mealRatios[mealType] ?? 1 / 3;
          const main = updatedDayMeals[mealType]?.main;
          const snack = updatedDayMeals[mealType]?.snack;
          if (main) {
            if (userInput?.constraint_type === "total") {
              const totalCalories =
                (main?.calories ?? 0) + (snack?.calories ?? 0);
              const totalCost = (main?.price ?? 0) + (snack?.price ?? 0);

              main.original_cost = totalCost;
              main.original_calories = totalCalories;
            } else {
              // Daily constraint
              main.original_cost = ratio * userInput.budget;
              main.original_calories = ratio * userInput.calories;
            }
          }
        }
        return updatedDayMeals;
      });

      setMealPlan(updatedPlan);
      setDailySnacks(snacks);
    }
  }, [suggestionPlan, userInput]);

  const handleSelectMeal = (
    dayIndex,
    mealType,
    newMealRaw,
    isSnack = false
  ) => {
    const newMeal = {
      ...newMealRaw,
      id: newMealRaw._id || newMealRaw.id,
      name: newMealRaw.name || newMealRaw.title,
      image: newMealRaw.image || newMealRaw.main_image,
      calories: newMealRaw.calories ?? newMealRaw.energy ?? 0,
      price: newMealRaw.price ?? 0,
    };

    const newPlan = [...mealPlan];
    newPlan[dayIndex] = { ...newPlan[dayIndex] };
    newPlan[dayIndex][mealType] = {
      ...newPlan[dayIndex][mealType],
      [isSnack ? "snack" : "main"]: newMeal,
    };

    console.log("🍱 newPlan[dayIndex]:", newPlan[dayIndex]);

    const newCalories = defaultMeals.reduce((acc, type) => {
      const mainMeal = newPlan[dayIndex][type]?.main;
      const snackMeal = newPlan[dayIndex][type]?.snack;

      const mainCals = mainMeal?.calories ?? 0;
      const snackCals =
        dailySnacks[dayIndex]?.[type] && snackMeal
          ? snackMeal.calories ?? 0
          : 0;

      return acc + mainCals + snackCals;
    }, 0);

    const newCost = defaultMeals.reduce((acc, type) => {
      const mainMeal = newPlan[dayIndex][type]?.main;
      const snackMeal = newPlan[dayIndex][type]?.snack;

      const mainCost = mainMeal?.price ?? 0;
      const snackCost =
        dailySnacks[dayIndex]?.[type] && snackMeal ? snackMeal.price ?? 0 : 0;

      return acc + mainCost + snackCost;
    }, 0);

    if (newCalories > calories || newCost > budget) {
      alert("Vượt giới hạn calo hoặc chi phí cho ngày này!");
      return;
    }

    setMealPlan(newPlan);
    setShowOptions({});
  };

  const toggleOptionList = async (dayIndex, mealType, isSnack = false) => {
    const key = `${dayIndex}-${mealType}-${isSnack ? "snack" : "main"}`;
    const dayMeals = mealPlan[dayIndex];
    const currentMeal = dayMeals?.[mealType]?.[isSnack ? "snack" : "main"];
    const isCurrentlyOpen = showOptions[key];
    const mealId = currentMeal._id || currentMeal.id;

    console.log("CLICKED TOGGLE:", { key, currentMeal });

    if (isCurrentlyOpen) {
      setShowOptions({});
    } else {
      setShowOptions({ [key]: true });

      // !mealOptions[key] && mealId
      if (mealId) {
        const calorieLimit =
          currentMeal?.original_calories ?? currentMeal?.calories;
        const priceLimit = currentMeal?.original_cost ?? currentMeal?.price;
        console.log("Gọi API get similar meals for:", mealId);
        try {
          const params = new URLSearchParams();
          params.append("calories", calorieLimit);
          params.append("price", priceLimit);
          allergens.forEach((a) => params.append("allergens", a));
          const res = await axios.get(
            `${process.env.REACT_APP_API_URL}/api/meals/similar/${mealId}?${params.toString()}`
          );
          console.log("API response:", res.data);
          console.log("Sample item:", res.data[0]);
          setMealOptions((prev) => ({
            ...prev,
            [key]: res.data,
          }));
        } catch (error) {
          console.error("Lỗi khi lấy món tương tự:", error);
        }
      } else {
        console.log("Không gọi API vì thiếu _id");
      }
    }
  };

  const handleSaveMealPlan = async () => {
    try {
      const selectedDate = new Date().toISOString();
      const token = localStorage.getItem("token");

      if (!token || !user) {
        alert("Vui lòng đăng nhập để lưu thực đơn!");
        return;
      }

      const cleanedPlan = mealPlan.map((dayMeals, dayIndex) => {
        const cleaned = {};

        defaultMeals.forEach((mealType) => {
          const mealData = dayMeals[mealType];
          const isSnackVisible = dailySnacks[dayIndex]?.[mealType];

          // Nếu không có snack hoặc snack toggle đang tắt, loại bỏ snack
          const cleanedMeal = {
            main: mealData.main,
            snack: isSnackVisible ? mealData.snack : null,
          };

          cleaned[mealType] = cleanedMeal;
        });

        return cleaned;
      });
      // console.log("🧾 cleanedPlan to save:", JSON.stringify(cleanedPlan, null, 2));

      const payload = {
        plan: cleanedPlan,
        date: selectedDate,
      };

      const res = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/meals_history/save`,
        payload,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (res.status === 200) {
        alert("Đã lưu thực đơn vào lịch sử!");
      } else {
        console.error("❌ Server trả về lỗi:", res.data);
        alert("Có lỗi khi lưu thực đơn.");
      }
    } catch (err) {
      console.error("❌ Lỗi khi lưu thực đơn:", err);
      alert("Lưu thực đơn thất bại.");
    }
  };

  return (
    <div className="meal-suggestion-wrapper container-fluid mt-4 px-0">
      <h2 className="text-center mb-3">📅 Thực đơn gợi ý</h2>
      <div className="meal-days-scroll-container">
        {mealPlan.map((dayMeals, dayIndex) => (
          <div className="day-column" key={dayIndex}>
            <div className="card h-100 p-2 shadow-sm">
              <h5 className="text-center mb-2 text-primary">
                Ngày {dayIndex + 1}
              </h5>

              {defaultMeals.map((mealType) => {
                const isSnackVisible = dailySnacks[dayIndex]?.[mealType];
                const mainKey = `${dayIndex}-${mealType}-main`;
                const snackKey = `${dayIndex}-${mealType}-snack`;

                // Tạo key ref cho snack
                const refKey = `${dayIndex}-${mealType}`;
                if (!snackRefs.current[refKey]) {
                  snackRefs.current[refKey] = React.createRef();
                }

                return (
                  <React.Fragment key={mealType}>
                    <div className="meal-row mb-2">
                      <strong>{mealType}</strong>
                      {dayMeals[mealType]?.main && (
                        <MealCard
                          key={`main-${mainKey}`}
                          meal={dayMeals[mealType].main}
                          onToggleList={() =>
                            toggleOptionList(dayIndex, mealType, false)
                          }
                          showOptions={showOptions[mainKey]}
                          isOptionOpen={showOptions[mainKey]}
                          options={mealOptions[mainKey] || []}
                          onSelect={(meal) =>
                            handleSelectMeal(dayIndex, mealType, meal, false)
                          }
                          onClickDetail={openMealDetail}
                          calorieLimit={
                            dayMeals[mealType].main?.original_calories
                          }
                          priceLimit={dayMeals[mealType].main?.original_cost}
                          type="main"
                        />
                      )}
                      {/* {(dayMeals[mealType]?.main || []).map((mainMeal, index) => (
                        <MealCard
                          key={`main-${mainKey}-${index}`}
                          meal={mainMeal}
                          onToggleList={() =>
                            toggleOptionList(dayIndex, mealType, false, index)
                          }
                          showOptions={showOptions[mainKey]}
                          isOptionOpen={showOptions[mainKey]}
                          options={mealOptions[mainKey] || []}
                          onSelect={(meal) =>
                            handleSelectMeal(dayIndex, mealType, meal, false)
                          }
                          onClickDetail={openMealDetail}
                        />
                      ))} */}
                    </div>

                    <div className="meal-divider">
                      <button
                        className="toggle-snack-btn"
                        onClick={() => toggleSnack(dayIndex, mealType)}
                      >
                        {isSnackVisible ? "−" : "+"}
                      </button>
                      <hr
                        className={
                          !isSnackVisible ? "visible-line" : "hidden-line"
                        }
                      />
                    </div>

                    <CSSTransition
                      in={isSnackVisible}
                      timeout={300}
                      classNames="slide-snack"
                      unmountOnExit
                      nodeRef={snackRefs.current[refKey]}
                    >
                      <div
                        ref={snackRefs.current[refKey]}
                        className="snack-meal-container"
                      >
                        <div className="snack-meal-row ms-3">
                          <strong>Phụ bữa {mealType}</strong>
                          {dayMeals[mealType]?.snack && (
                            <MealCard
                              key={`snack-${snackKey}`}
                              meal={dayMeals[mealType].snack}
                              onToggleList={() =>
                                toggleOptionList(dayIndex, mealType, true)
                              }
                              showOptions={showOptions[snackKey]}
                              isOptionOpen={showOptions[snackKey]}
                              options={mealOptions[snackKey] || []}
                              onSelect={(meal) =>
                                handleSelectMeal(dayIndex, mealType, meal, true)
                              }
                              onClickDetail={openMealDetail}
                              type="snack"
                            />
                          )}
                        </div>
                      </div>
                    </CSSTransition>
                  </React.Fragment>
                );
              })}

              <hr className="final-divider mb-2 mt-1" />
              <div className="summary-footer text-center">
                <p className="mb-1">
                  <strong>Tổng calo:</strong>{" "}
                  {defaultMeals.reduce((sum, type) => {
                    const mainMeal = dayMeals[type]?.main;
                    const snackMeal = dailySnacks[dayIndex]?.[type]
                      ? dayMeals[type]?.snack
                      : null;

                    return (
                      sum +
                      (mainMeal?.calories || 0) +
                      (snackMeal?.calories || 0)
                    );
                  }, 0)}{" "}
                  kcal
                </p>
                <p>
                  <strong>Tổng chi phí:</strong>{" "}
                  {defaultMeals
                    .reduce((sum, type) => {
                      const mainMeal = dayMeals[type]?.main;
                      const snackMeal = dailySnacks[dayIndex]?.[type]
                        ? dayMeals[type]?.snack
                        : null;

                      return (
                        sum + (mainMeal?.price || 0) + (snackMeal?.price || 0)
                      );
                    }, 0)
                    .toLocaleString()}
                  ₫
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <MealDetailModal
        show={showDetailModal}
        onHide={() => setShowDetailModal(false)}
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

      {showLoginModal && (
        <ModalLogin
          show={showLoginModal}
          handleClose={() => setShowLoginModal(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      )}

      {user && (
        <div className="text-center mt-4">
          <Button variant="success" onClick={handleSaveMealPlan}>
            💾 Lưu thực đơn
          </Button>
        </div>
      )}
    </div>
  );
};

export default MealSuggestionResult;

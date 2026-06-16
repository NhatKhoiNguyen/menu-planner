import mockMeals from "./mockMeals";

export function generateMealPlan({
  calories,
  budget,
  preferences,
  numDays,
  mainMeals,
  budgetType,
  allergens,
  allowFallback = false,
}) {
  const calorieLimit = parseInt(calories);
  const budgetLimit = parseInt(budget);
  const dailyBudget =
    budgetType === "perDay" ? budgetLimit : Math.floor(budgetLimit / numDays);
  const dailyCalorieLimit = calorieLimit;

  const preferenceSet = new Set(preferences);
  const allergenKeywords = {
    Trứng: ["trứng"],
    "Hải sản": ["tôm", "mực", "cá", "hải sản"],
    Sữa: ["sữa", "phô mai", "kem", "bơ"],
    "Đậu phộng": ["đậu phộng", "bơ đậu phộng"],
    "Đậu nành": ["đậu nành", "đậu hũ", "nước tương"],
    "Lúa mì": ["bột mì", "mì", "bánh mì", "lúa mì"],
  };

  const filteredMeals = mockMeals.filter((meal) => {
    const matchPreferences =
      preferences.length === 0 ||
      meal.tags.some((tag) => preferenceSet.has(tag));

    const matchAllergens =
      allergens.length === 0 ||
      !meal.ingredients.some((ingredient) => {
        return allergens.some((allergen) =>
          (allergenKeywords[allergen] || []).some((keyword) =>
            ingredient.toLowerCase().includes(keyword),
          ),
        );
      });

    return matchPreferences && matchAllergens;
  });

  const getRandomMeal = (type, calTarget) => {
    const candidates = filteredMeals
      .filter((m) => m.type === type)
      .sort(() => 0.5 - Math.random());

    for (let meal of candidates) {
      if (
        meal.calories >= calTarget - 100 &&
        meal.calories <= calTarget + 100
      ) {
        return meal;
      }
    }

    if (allowFallback) {
      return candidates.sort((a, b) => a.price - b.price)[0] || null;
    }

    return null;
  };

  const plan = [];
  const totalCalSplit = { Sáng: 0.25, Trưa: 0.4, Tối: 0.35 };

  let totalCals = 0;
  let totalCost = 0;

  for (let day = 0; day < numDays; day++) {
    const dayMeals = {};
    let dayCals = 0;
    let dayCost = 0;

    for (let mealName of mainMeals) {
      const mealCaloriesTarget = dailyCalorieLimit * totalCalSplit[mealName];

      const mainMeal = getRandomMeal("main", mealCaloriesTarget);
      const snack = getRandomMeal("snack", 150);

      const mainCalories = mainMeal ? mainMeal.calories : 0;
      const snackCalories = snack ? snack.calories : 0;
      const mainPrice = mainMeal ? mainMeal.price : 0;
      const snackPrice = snack ? snack.price : 0;

      const predictedDayCost = dayCost + mainPrice + snackPrice;
      const predictedTotalCost = totalCost + mainPrice + snackPrice;

      const predictedTotalCals = totalCals + mainCalories + snackCalories;

      // Nếu vượt giới hạn theo kiểu budget
      const overBudget =
        (budgetType === "perDay" && predictedDayCost > dailyBudget) ||
        (budgetType === "total" && predictedTotalCost > budgetLimit);

      const overCalories = predictedTotalCals > calorieLimit * numDays;

      if (overBudget || overCalories) {
        dayMeals[mealName] = { main: null, snack: null };
        continue;
      }

      // Thêm món nếu không vượt
      dayMeals[mealName] = {
        main: mainMeal,
        snack: snack,
      };

      dayCals += mainCalories + snackCalories;
      dayCost += mainPrice + snackPrice;
      totalCals += mainCalories + snackCalories;
      totalCost += mainPrice + snackPrice;
    }

    plan.push({
      day: day + 1,
      meals: dayMeals,
      calories: dayCals,
      price: dayCost,
      withinDailyBudget:
        budgetType === "perDay" ? dayCost <= dailyBudget : true,
    });
  }

  return {
    plan,
    totalCalories: totalCals,
    totalPrice: totalCost,
    withinBudget: totalCost <= budgetLimit,
    withinCalories: totalCals <= calorieLimit * numDays,
  };
}

import React, { useEffect, useState, useCallback } from "react";
import { Form, Container, Row, Col, Button } from "react-bootstrap";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

const Statistics = () => {
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [selectedMeals, setSelectedMeals] = useState({
    breakfast: true,
    lunch: true,
    dinner: true,
  });
  const [topStats, setTopStats] = useState([]);
  const [bottomStats, setBottomStats] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [availableMeals, setAvailableMeals] = useState([]);
  const [selectedTrendMeals, setSelectedTrendMeals] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  const token = localStorage.getItem("token");

  const formatDateVN = (date) => {
    if (!date) return "";
    const tzOffset = 7 * 60 * 60 * 1000; // UTC+7 in milliseconds
    const local = new Date(date.getTime() + tzOffset);
    return local.toISOString().split("T")[0]; // yyyy-mm-dd
  };

  const handleMealToggle = (meal) => {
    setSelectedMeals((prev) => ({
      ...prev,
      [meal]: !prev[meal],
    }));
  };
  const selectedMealKeys = Object.entries(selectedMeals)
    .filter(([_, value]) => value)
    .map(([key]) => key)
    .join(",");

  const fetchStats = async () => {
    // const selectedMealKeys = Object.entries(selectedMeals)
    //   .filter(([_, value]) => value)
    //   .map(([key]) => key)
    //   .join(",");

    if (!startDate || !endDate || selectedMealKeys.length === 0) {
      alert("Vui lòng chọn ngày bắt đầu, kết thúc và ít nhất một bữa.");
      return;
    }

    try {
      const res = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/stats/most-selected`,
        {
          params: {
            start_date: formatDateVN(startDate),
            end_date: formatDateVN(endDate),
            meal_times: selectedMealKeys,
          },
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      setTopStats(res.data.top20 || []);
      setBottomStats(res.data.bottom20 || []);
      await fetchTrend();
    } catch (err) {
      console.error("Lỗi lấy thống kê:", err);
    }
  };

  //   const fetchTrend = async () => {
  //     try {
  //       const selectedTitles = selectedTrendMeals
  //         .map((id) => {
  //           const found = availableMeals.find((m) => m.id === id);
  //           return found?.title;
  //         })
  //         .filter(Boolean);
  //       const res = await axios.get(`${process.env.REACT_APP_API_URL}/api/stats/trend`, {
  //         params: {
  //           start_date: formatDateVN(startDate),
  //           end_date: formatDateVN(endDate),
  //           meal_times: selectedMealKeys,
  //           titles: selectedTrendMeals.join(","),
  //         },
  //         headers: { Authorization: `Bearer ${token}` },
  //       });
  //       setTrendData(res.data || []);
  //       console.log("Trend data response:", res.data);
  //     } catch (err) {
  //       console.error("Lỗi lấy dữ liệu xu hướng:", err);
  //     }
  //   };

  const fetchTrend = async () => {
    try {
      // Lấy danh sách titles từ selected IDs
      const selectedTitles = selectedTrendMeals
        .map((id) => availableMeals.find((meal) => meal.id === id)?.title)
        .filter(Boolean); // bỏ undefined

      console.log("Selected titles for trend:", selectedTitles);
      console.log("Sending params to trend API", {
        start_date: formatDateVN(startDate),
        end_date: formatDateVN(endDate),
        meal_times: selectedMealKeys,
        titles: selectedTitles.join(","),
      });

      const res = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/stats/trend`,
        {
          params: {
            start_date: formatDateVN(startDate),
            end_date: formatDateVN(endDate),
            meal_times: selectedMealKeys,
            titles: selectedTitles.join(","),
          },
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      console.log("Trend data response:", res.data);

      setTrendData(res.data || []);
    } catch (err) {
      console.error("Lỗi lấy dữ liệu xu hướng:", err);
    }
  };

  const fetchAvailableMeals = useCallback(async () => {
    try {
      const res = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/stats/trend/meals`,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      setAvailableMeals(res.data || []);
    } catch (err) {
      console.error("Lỗi lấy danh sách món:", err);
    }
  }, [token]);

  useEffect(() => {
    fetchAvailableMeals();
  }, [fetchAvailableMeals]);

  const transformChartData = (data) => {
    return data.map((item) => ({
      titleShort:
        item.title.length > 20 ? item.title.slice(0, 20) + "…" : item.title,
      titleFull: item.title,
      count: item.count,
    }));
  };

  const transformTrendData = (raw) => {
    const map = {};
    raw.forEach(({ date, title, count }) => {
      if (!map[date]) map[date] = { date };
      map[date][title] = count;
    });
    return Object.values(map);
  };

  const chartData = transformTrendData(trendData);
  console.log("Transformed chart data:", chartData);

  return (
    <Container className="mt-4">
      <h4>📊 Thống kê món ăn theo khoảng thời gian và bữa ăn</h4>

      <Row className="mb-3">
        <Col md={3}>
          <Form.Label>Ngày bắt đầu</Form.Label>
          <Form.Control
            type="date"
            value={startDate ? formatDateVN(startDate) : ""}
            onChange={(e) => setStartDate(new Date(e.target.value))}
          />
        </Col>
        <Col md={3}>
          <Form.Label>Ngày kết thúc</Form.Label>
          <Form.Control
            type="date"
            value={endDate ? formatDateVN(endDate) : ""}
            onChange={(e) => setEndDate(new Date(e.target.value))}
          />
        </Col>
        <Col md={6}>
          <Form.Label>Bữa ăn</Form.Label>
          <div>
            {["breakfast", "lunch", "dinner"].map((meal) => (
              <Form.Check
                key={meal}
                inline
                type="checkbox"
                label={
                  meal === "breakfast"
                    ? "Sáng"
                    : meal === "lunch"
                      ? "Trưa"
                      : "Tối"
                }
                checked={selectedMeals[meal]}
                onChange={() => handleMealToggle(meal)}
              />
            ))}
          </div>
        </Col>
        <Col md={12} className="mt-3">
          <Form.Label>Chọn món để xem xu hướng</Form.Label>
          <Form.Control
            type="text"
            placeholder="Tìm món..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="mb-2"
          />
          <div
            style={{
              maxHeight: "200px",
              overflowY: "auto",
              border: "1px solid #ccc",
              padding: "10px",
            }}
          >
            {availableMeals
              .filter((meal) =>
                meal.title.toLowerCase().includes(searchTerm.toLowerCase()),
              )
              .map((meal) => (
                <Form.Check
                  key={meal.id}
                  type="checkbox"
                  label={meal.title}
                  checked={selectedTrendMeals.includes(meal.id)}
                  onChange={(e) => {
                    setSelectedTrendMeals((prev) =>
                      e.target.checked
                        ? [...prev, meal.id]
                        : prev.filter((id) => id !== meal.id),
                    );
                  }}
                />
              ))}
          </div>
        </Col>
      </Row>

      <Button onClick={fetchStats} variant="primary" className="mb-4">
        Xem thống kê
      </Button>

      {topStats.length > 0 && (
        <>
          <h5 className="mb-3">🔝 Top 20 món được chọn nhiều nhất</h5>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={transformChartData(topStats)}
              margin={{ top: 20, right: 30, left: 10, bottom: 80 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="titleShort"
                tick={{ fontSize: 12, angle: -45, textAnchor: "end" }}
                interval={0}
              />
              <YAxis />
              <Tooltip
                formatter={(value) => [value, "Số lần được chọn"]}
                labelFormatter={(label, payload) =>
                  payload && payload.length > 0
                    ? `Món: ${payload[0].payload.titleFull}`
                    : ""
                }
              />
              <Legend />
              <Bar dataKey="count" fill="#82ca9d" name="Số lần được chọn" />
            </BarChart>
          </ResponsiveContainer>
        </>
      )}

      {bottomStats.length > 0 && (
        <>
          <h5 className="mt-5 mb-3">🔻 Top 20 món ít được chọn nhất</h5>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={transformChartData(bottomStats)}
              margin={{ top: 20, right: 30, left: 10, bottom: 80 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="titleShort"
                tick={{ fontSize: 12, angle: -45, textAnchor: "end" }}
                interval={0}
              />
              <YAxis />
              <Tooltip
                formatter={(value) => [value, "Số lần được chọn"]}
                labelFormatter={(label, payload) =>
                  payload && payload.length > 0
                    ? `Món: ${payload[0].payload.titleFull}`
                    : ""
                }
              />
              <Legend />
              <Bar dataKey="count" fill="#ff7f50" name="Số lần được chọn" />
            </BarChart>
          </ResponsiveContainer>
        </>
      )}

      {chartData.length > 0 && (
        <>
          <h5 className="mt-5 mb-3">📈 Xu hướng chọn món theo ngày</h5>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              {Object.keys(chartData[0] || {})
                .filter((k) => k !== "date")
                .map((key, idx) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={`hsl(${(idx * 45) % 360}, 70%, 50%)`}
                    dot={false}
                  />
                ))}
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </Container>
  );
};

export default Statistics;

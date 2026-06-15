import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import { publicRoutes, privateRoutes } from './routes';
import PrivateRoute from './components/PrivateRoute';
import Header from "./components/Header";
import { UserContext } from "./contexts/UserContext";
import './styles/AppLayout.css';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

function App() {
  const { user, setUser } = useContext(UserContext);

  return (
    <Router>
      <div className="App">
        <Header user={user} setUser={setUser} />
        <Routes>
          {publicRoutes.map((route, index) => {
            const Page = route.component;
            return (
              <Route
                key={index}
                path={route.path}
                element={<Page />}
              />
            );
          })}
          {privateRoutes.map((route, index) => {
            const Page = route.component;
            return (
              <Route
                key={index}
                path={route.path}
                element={
                  <PrivateRoute roles={route.roles}>
                    <Page />
                  </PrivateRoute>
                }
              />
            );
          })}
        </Routes>
      </div>
      <ToastContainer position="top-right" autoClose={3000} />
    </Router>
    
  );
}

export default App;

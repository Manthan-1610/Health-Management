import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import App from "./App";
import Layout from "./components/Layout";
import NoMatch from "./components/NoMatch";
import ImageUpload from "./components/ImageUpload";
import "./styles/index.css";
import MedicineInventory from "./components/MedicineInventory";
import Login from './components/Login';
import Signup from './components/Signup';
import FamilyGroup from "./components/FamilyGroup";
import Dashboard from "./components/Dashboard";
import ForgotPassword from "./components/ForgotPassword";
import ResetPassword from "./components/ResetPassword";
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<App />} />
            <Route path="/image" element={<ImageUpload />}></Route>
            <Route path="/inventory" element={<MedicineInventory />}></Route>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/familygroup" element={<FamilyGroup />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />
          </Route>
          <Route path="*" element={<NoMatch />} />
        </Routes>
      </BrowserRouter>
  </React.StrictMode>
);

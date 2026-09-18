import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/MainLayout';
import Dashboard from './views/Dashboard';
import QuranicRings from './views/QuranicRings';
import Sessions from './views/Sessions';
import Students from './views/Students';
import Login from './views/Login';
import Register from './views/Register';
import AdminReports from './views/AdminReports';
import Teachers from './views/Teachers';
import Users from './views/Users';
import PlaceholderView from './views/PlaceholderView';
import './index.css';

// Guard: يحمي المسارات التي تحتاج تسجيل دخول
const PrivateRoute = ({ children }) => {
    const token = localStorage.getItem('access_token');
    return token ? children : <Navigate to="/login" replace />;
};

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));

    const handleLoginSuccess = () => {
        setIsLoggedIn(true);
    };

    return (
        <BrowserRouter>
            <Routes>
                {/* صفحة تسجيل الدخول */}
                <Route
                    path="/login"
                    element={
                        isLoggedIn
                            ? <Navigate to="/dashboard" replace />
                            : <Login onLoginSuccess={handleLoginSuccess} />
                    }
                />

                {/* صفحة تسجيل مسجد جديد (عامة) */}
                <Route path="/register" element={<Register />} />

                {/* المسارات المحمية */}
                <Route
                    path="/"
                    element={
                        <PrivateRoute>
                            <MainLayout />
                        </PrivateRoute>
                    }
                >
                    <Route index element={<Navigate to="/dashboard" replace />} />
                    <Route path="dashboard" element={<Dashboard />} />
                    <Route path="users" element={<Users />} />
                    <Route path="projects" element={<PlaceholderView title="المشاريع" />} />
                    <Route path="students" element={<Students />} />
                    <Route path="teachers" element={<Teachers />} />
                    <Route path="rings" element={<QuranicRings />} />
                    <Route path="centers" element={<PlaceholderView title="المراكز" />} />
                    <Route path="sessions" element={<Sessions />} />
                    <Route path="rewards" element={<PlaceholderView title="النقاط والمكافآت" />} />
                    <Route path="reports" element={<AdminReports />} />
                    <Route path="settings" element={<PlaceholderView title="الإعدادات" />} />
                </Route>

                {/* أي مسار غير معروف */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;


import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Dashboard from './components/Dashboard';
import CarForm from './components/CarForm';
import InsuranceForm from './components/InsuranceForm';
import ServiceForm from './components/ServiceForm';
import RefuelingForm from './components/RefuelingForm';
import CarDetails from './components/CarDetails';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import PublicDashboard from './components/PublicDashboard';
import AddVignette from './components/AddVignette';
import CarEditForm from './components/CarEditForm';

const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  if (loading) return <div className="text-center p-20 text-blue-600">Checking auth...</div>;
  if (!token) return <Navigate to="/login" />;
  return children;
};

const NavBar = () => {
  const { token, user, logout } = useAuth();
  return (
    <nav className="bg-slate-900 text-white p-4 shadow-xl">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-black tracking-tighter hover:text-blue-400 transition flex items-center">
          <span className="mr-2">🚗</span> CAR TRACKER
        </Link>
        <div className="flex items-center space-x-6 font-medium">
          {token ? (
            <>
              <Link to="/home" className="hover:text-blue-400">My Garage</Link>
              <span className="text-gray-500 text-sm">Hi, {user?.email}</span>
              <button onClick={logout} className="bg-red-500/10 text-red-400 px-4 py-2 rounded-lg hover:bg-red-500 hover:text-white transition text-sm">Logout</button>
            </>
          ) : (
            <>
              <Link to="/" className="hover:text-blue-400">Stats</Link>
              <Link to="/login" className="hover:text-blue-400">Login</Link>
              <Link to="/register" className="bg-blue-600 px-5 py-2 rounded-full hover:bg-blue-500 transition">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
          <NavBar />
          <main className="container mx-auto p-4 md:p-8">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<PublicDashboard />} />
              <Route path="/login" element={<LoginForm />} />
              <Route path="/register" element={<RegisterForm />} />

              {/* Protected Protected Routes */}
              <Route path="/home" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/add-car" element={<ProtectedRoute><CarForm /></ProtectedRoute>} />
              <Route path="/cars/:id" element={<ProtectedRoute><CarDetails /></ProtectedRoute>} />
              <Route path="/cars/:id/add-insurance" element={<ProtectedRoute><InsuranceForm /></ProtectedRoute>} />
              <Route path="/cars/:id/add-service" element={<ProtectedRoute><ServiceForm /></ProtectedRoute>} />
              <Route path="/cars/:id/add-refueling" element={<ProtectedRoute><RefuelingForm /></ProtectedRoute>} />
              <Route path="/cars/:id/add-vignette" element={<ProtectedRoute><AddVignette /></ProtectedRoute>} />
              <Route path="/cars/:id/edit" element={<ProtectedRoute><CarEditForm /></ProtectedRoute>} />

              {/* Catch-all */}
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

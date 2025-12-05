import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Consumos from './pages/Consumos'
import Reportes from './pages/Reportes'
import Usuarios from './pages/admin/Usuarios'
import Hospitales from './pages/admin/Hospitales'
import Gases from './pages/admin/Gases'
import Auditoria from './pages/admin/Auditoria'
import ProtectedRoute from './components/shared/ProtectedRoute'

function App() {
  return (
    <Router>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            iconTheme: {
              primary: '#28a745',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#dc3545',
              secondary: '#fff',
            },
          },
        }}
      />
      
      <Routes>
        {/* Rutas públicas */}
        <Route path="/login" element={<Login />} />
        
        {/* Rutas protegidas */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/consumos" 
          element={
            <ProtectedRoute>
              <Consumos />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/reportes" 
          element={
            <ProtectedRoute>
              <Reportes />
            </ProtectedRoute>
          } 
        />
        
        {/* Rutas admin */}
        <Route 
          path="/admin/usuarios" 
          element={
            <ProtectedRoute adminOnly>
              <Usuarios />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/admin/hospitales" 
          element={
            <ProtectedRoute adminOnly>
              <Hospitales />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/admin/gases" 
          element={
            <ProtectedRoute adminOnly>
              <Gases />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/admin/auditoria" 
          element={
            <ProtectedRoute adminOnly>
              <Auditoria />
            </ProtectedRoute>
          } 
        />
        
        {/* Redirección por defecto */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App

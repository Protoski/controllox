// API Service - Frontend
// Sistema de Gases Medicinales MSPBS

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Crear instancia de axios
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ AUTENTICACIÓN ============
export const authService = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.usuario));
    }
    
    return response.data;
  },
  
  logout: async () => {
    await api.post('/auth/logout');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  
  recuperarPassword: async (email) => {
    return await api.post('/auth/recuperar-password', { email });
  },
  
  resetPassword: async (token, newPassword) => {
    return await api.post('/auth/reset-password', {
      token,
      new_password: newPassword
    });
  }
};

// ============ USUARIOS ============
export const usuariosService = {
  listar: async (params = {}) => {
    const response = await api.get('/usuarios/', { params });
    return response.data;
  },
  
  crear: async (usuario) => {
    const response = await api.post('/usuarios/', usuario);
    return response.data;
  },
  
  obtener: async (id) => {
    const response = await api.get(`/usuarios/${id}`);
    return response.data;
  },
  
  actualizar: async (id, usuario) => {
    const response = await api.put(`/usuarios/${id}`, usuario);
    return response.data;
  },
  
  cambiarPassword: async (id, newPassword) => {
    const response = await api.post(`/usuarios/${id}/change-password`, null, {
      params: { new_password: newPassword }
    });
    return response.data;
  },
  
  yo: async () => {
    const response = await api.get('/usuarios/me');
    return response.data;
  }
};

// ============ HOSPITALES ============
export const hospitalesService = {
  listar: async (params = {}) => {
    const response = await api.get('/hospitales/', { params });
    return response.data;
  },
  
  crear: async (hospital) => {
    const response = await api.post('/hospitales/', hospital);
    return response.data;
  },
  
  obtener: async (id) => {
    const response = await api.get(`/hospitales/${id}`);
    return response.data;
  },
  
  actualizar: async (id, hospital) => {
    const response = await api.put(`/hospitales/${id}`, hospital);
    return response.data;
  },
  
  estadisticas: async (id, params = {}) => {
    const response = await api.get(`/hospitales/${id}/estadisticas`, { params });
    return response.data;
  },
  
  departamentos: async () => {
    const response = await api.get('/hospitales/departamentos');
    return response.data;
  }
};

// ============ GASES ============
export const gasesService = {
  listar: async (params = {}) => {
    const response = await api.get('/gases/', { params });
    return response.data;
  },
  
  crear: async (gas) => {
    const response = await api.post('/gases/', gas);
    return response.data;
  },
  
  obtener: async (id) => {
    const response = await api.get(`/gases/${id}`);
    return response.data;
  },
  
  actualizar: async (id, gas) => {
    const response = await api.put(`/gases/${id}`, gas);
    return response.data;
  }
};

// ============ CONSUMOS ============
export const consumosService = {
  listar: async (params = {}) => {
    const response = await api.get('/consumos/', { params });
    return response.data;
  },
  
  crear: async (consumo) => {
    const response = await api.post('/consumos/', consumo);
    return response.data;
  },
  
  obtener: async (id) => {
    const response = await api.get(`/consumos/${id}`);
    return response.data;
  },
  
  actualizar: async (id, consumo) => {
    const response = await api.put(`/consumos/${id}`, consumo);
    return response.data;
  },
  
  eliminar: async (id) => {
    const response = await api.delete(`/consumos/${id}`);
    return response.data;
  },
  
  validar: async (id) => {
    const response = await api.post(`/consumos/${id}/validar`);
    return response.data;
  }
};

// ============ REPORTES ============
export const reportesService = {
  dashboardAdmin: async (params = {}) => {
    const response = await api.get('/reportes/dashboard', { params });
    return response.data;
  },
  
  dashboardHospital: async (params = {}) => {
    const response = await api.get('/reportes/dashboard/hospital', { params });
    return response.data;
  },
  
  generarPDF: async (filtros, tipoReporte = 'global') => {
    const response = await api.post('/reportes/generar-pdf', filtros, {
      params: { tipo_reporte: tipoReporte },
      responseType: 'blob'
    });
    
    // Crear URL del blob y descargar
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `reporte_${tipoReporte}_${Date.now()}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    
    return response.data;
  },
  
  generarExcel: async (filtros, formato = 'xlsx') => {
    const response = await api.post('/reportes/generar-excel', filtros, {
      params: { formato },
      responseType: 'blob'
    });
    
    // Crear URL del blob y descargar
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `reporte_consumos_${Date.now()}.${formato}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    
    return response.data;
  },
  
  consumoMensual: async (params = {}) => {
    const response = await api.get('/reportes/consumo-mensual', { params });
    return response.data;
  }
};

// ============ AUDITORÍA ============
export const auditoriaService = {
  listar: async (params = {}) => {
    const response = await api.get('/auditoria/', { params });
    return response.data;
  },
  
  estadisticas: async (params = {}) => {
    const response = await api.get('/auditoria/estadisticas', { params });
    return response.data;
  },
  
  acciones: async () => {
    const response = await api.get('/auditoria/acciones');
    return response.data;
  }
};

export default api;

import { useEffect, useRef } from 'react';
import api from '../../api/axiosClient'; 

const useTokenRefresher = () => {
  const lastActivityRef = useRef(Date.now());
  const isRefreshingRef = useRef(false);

  useEffect(() => {
    // 1. Detectar actividad del usuario en la interfaz
    const handleUserActivity = () => {
      lastActivityRef.current = Date.now();
    };

    window.addEventListener('mousemove', handleUserActivity);
    window.addEventListener('keydown', handleUserActivity);
    window.addEventListener('click', handleUserActivity);

    // 2. Revisar cada 5 minutos si se debe renovar el token
    const intervalId = setInterval(async () => {
      const inactivityTime = Date.now() - lastActivityRef.current;
      const TWENTY_MINUTES = 20 * 60 * 1000; // Umbral de inactividad (20 min)

      // Si el usuario ha estado activo y no hay otra petición de refresh en curso
      if (inactivityTime < TWENTY_MINUTES && !isRefreshingRef.current) {
        try {
          isRefreshingRef.current = true;
          
          // Petición silenciosa: la cookie viaja gracias a withCredentials: true
          await api.post('/auth/refresh');
          
        } catch (error) {
          // Si el backend responde con 401, el interceptor de tu axiosClient 
          // se encargará automáticamente de limpiar y redirigir al login.
          console.debug('No se pudo renovar la sesión de forma automática.');
        } finally {
          isRefreshingRef.current = false;
        }
      }
    }, 5 * 60 * 1000); // Se ejecuta cada 5 minutos

    // Limpieza de eventos al desmontar
    return () => {
      window.removeEventListener('mousemove', handleUserActivity);
      window.removeEventListener('keydown', handleUserActivity);
      window.removeEventListener('click', handleUserActivity);
      clearInterval(intervalId);
    };
  }, []);
};

export default useTokenRefresher;
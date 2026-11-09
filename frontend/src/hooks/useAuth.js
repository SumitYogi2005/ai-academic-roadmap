import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import apiClient from '../lib/axios';
import { useAuthStore } from '../store/authStore';

export function useLogin() {
  const { login } = useAuthStore();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async ({ email, password }) => {
      // FastAPI OAuth2 expects form data
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      const { data } = await apiClient.post('/api/v1/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      return data;
    },
    onSuccess: (data) => {
      login(data.user, data.access_token);
      navigate('/dashboard');
    },
  });
}

export function useRegister() {
  const { login } = useAuthStore();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await apiClient.post('/api/v1/auth/register', payload);
      return data;
    },
    onSuccess: (data) => {
      login(data.user, data.access_token);
      navigate('/onboarding');
    },
  });
}

export function useLogout() {
  const { logout } = useAuthStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return () => {
    logout();
    queryClient.clear();
    navigate('/login');
  };
}

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import { EmailAuthToken, User } from '@/types/api/accounts';

export const useAuth = () => {
  const queryClient = useQueryClient();

  const login = useMutation({
    mutationFn: async (credentials: EmailAuthToken) => {
      const response = await apiClient.post('/accounts/auth/token/', credentials);
      return response.data;
    },
    onSuccess: (data) => {
      if (data.token) {
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
      }
    },
  });

  // User registration
  const register = useMutation({
    mutationFn: async (userData: User) => {
      const response = await apiClient.post('/accounts/users/', userData);
      return response.data;
    },
  });

  // Logout
  const logout = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/accounts/users/logout/', {});
      return response.data;
    },
    onSuccess: () => {
      // Clear token and user data
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      // Clear cached queries
      queryClient.clear();
    },
  });

  // Request password reset
  const requestPasswordReset = useMutation({
    mutationFn: async (email: string) => {
      const response = await apiClient.post('/accounts/users/reset_password_request/', { email });
      return response.data;
    },
  });

  // Confirm password reset
  const confirmPasswordReset = useMutation({
    mutationFn: async (data: { token: string; password: string; password_confirmation: string }) => {
      const response = await apiClient.post('/accounts/users/reset_password_confirm/', data);
      return response.data;
    },
  });

  // Change password (for logged-in users)
  const changePassword = useMutation({
    mutationFn: async (data: { current_password?: string; password: string; password_confirmation: string }) => {
      const response = await apiClient.post('/accounts/users/change_password/', data);
      return response.data;
    },
  });

  return {
    login,
    register,
    logout,
    requestPasswordReset,
    confirmPasswordReset,
    changePassword,
    isAuthenticated: !!localStorage.getItem('auth_token'),
  };
};
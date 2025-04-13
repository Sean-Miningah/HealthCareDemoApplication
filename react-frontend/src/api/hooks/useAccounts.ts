import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import { User, UserUpdateRequest } from '@/types/api/accounts';

export const useAccounts = () => {
  const queryClient = useQueryClient();

  // Get current user profile
  const useCurrentUser = () => {
    return useQuery({
      queryKey: ['currentUser'],
      queryFn: async () => {
        const response = await apiClient.get('/accounts/users/me/');
        // The API returns an array with user data
        return response.data[0];
      },
      // Skip if not authenticated
      enabled: !!localStorage.getItem('auth_token'),
    });
  };

  // Get all users (admin only)
  const useUsers = () => {
    return useQuery({
      queryKey: ['users'],
      queryFn: async () => {
        const response = await apiClient.get('/accounts/users/');
        return response.data;
      },
    });
  };

  // Get user by ID
  const useUser = (id: string) => {
    return useQuery({
      queryKey: ['user', id],
      queryFn: async () => {
        const response = await apiClient.get(`/accounts/users/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  // Update current user profile
  const updateProfile = useMutation({
    mutationFn: async (userData: UserUpdateRequest) => {
      const response = await apiClient.put('/accounts/users/update_profile/', userData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });

  // Update user (admin)
  const updateUser = useMutation({
    mutationFn: async ({ id, userData }: { id: string; userData: Partial<User> }) => {
      const response = await apiClient.put(`/accounts/users/${id}/`, userData);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['user', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  // Delete user (admin)
  const deleteUser = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/accounts/users/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  return {
    useCurrentUser,
    useUsers,
    useUser,
    updateProfile,
    updateUser,
    deleteUser,
  };
};
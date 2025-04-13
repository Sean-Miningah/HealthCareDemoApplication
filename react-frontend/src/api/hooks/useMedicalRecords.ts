import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import {
  // MedicalRecord,
  MedicalRecordCreate,
  MedicalRecordUpdate,
  // MedicalRecordAccess,
  MedicalImage,
  MedicalImageUpdate,
  AddImageRequest,
} from '@/types/api/medical-records';

export const useMedicalRecords = () => {
  const queryClient = useQueryClient();

  // Fetch all medical records
  const useAllMedicalRecords = () => {
    return useQuery({
      queryKey: ['medicalRecords'],
      queryFn: async () => {
        const response = await apiClient.get('/medical-records/medical-records/');
        return response.data;
      },
    });
  };

  // Fetch my medical records (for patients)
  const useMyMedicalRecords = () => {
    return useQuery({
      queryKey: ['myMedicalRecords'],
      queryFn: async () => {
        const response = await apiClient.get('/medical-records/medical-records/my_records/');
        return response.data;
      },
      enabled: !!localStorage.getItem('auth_token'),
    });
  };

  // Fetch single medical record
  const useMedicalRecord = (id: string) => {
    return useQuery({
      queryKey: ['medicalRecord', id],
      queryFn: async () => {
        const response = await apiClient.get(`/medical-records/medical-records/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  // Create medical record
  const createMedicalRecord = useMutation({
    mutationFn: async (data: MedicalRecordCreate) => {
      const response = await apiClient.post('/medical-records/medical-records/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medicalRecords'] });
      queryClient.invalidateQueries({ queryKey: ['myMedicalRecords'] });
    },
  });

  // Update medical record
  const updateMedicalRecord = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: MedicalRecordUpdate }) => {
      const response = await apiClient.put(`/medical-records/medical-records/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['medicalRecord', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['medicalRecords'] });
      queryClient.invalidateQueries({ queryKey: ['myMedicalRecords'] });
    },
  });

  // Delete medical record
  const deleteMedicalRecord = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/medical-records/medical-records/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medicalRecords'] });
      queryClient.invalidateQueries({ queryKey: ['myMedicalRecords'] });
    },
  });

  // Medical Record Access Logs
  const useMedicalRecordAccessLogs = (recordId: string) => {
    return useQuery({
      queryKey: ['medicalRecordAccessLogs', recordId],
      queryFn: async () => {
        const response = await apiClient.get(`/medical-records/medical-records/${recordId}/access_logs/`);
        return response.data;
      },
      enabled: !!recordId,
    });
  };

  const useAllAccessLogs = () => {
    return useQuery({
      queryKey: ['allAccessLogs'],
      queryFn: async () => {
        const response = await apiClient.get('/medical-records/access-logs/');
        return response.data;
      },
    });
  };

  const useAccessLog = (id: string) => {
    return useQuery({
      queryKey: ['accessLog', id],
      queryFn: async () => {
        const response = await apiClient.get(`/medical-records/access-logs/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  // Medical Images
  const useAllMedicalImages = () => {
    return useQuery({
      queryKey: ['medicalImages'],
      queryFn: async () => {
        const response = await apiClient.get('/medical-records/medical-images/');
        return response.data;
      },
    });
  };

  const useMedicalImage = (id: string) => {
    return useQuery({
      queryKey: ['medicalImage', id],
      queryFn: async () => {
        const response = await apiClient.get(`/medical-records/medical-images/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  // Add image to a medical record
  const addImageToMedicalRecord = useMutation({
    mutationFn: async ({ recordId, data }: { recordId: string; data: AddImageRequest }) => {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('title', data.title);
      if (data.description) formData.append('description', data.description);
      formData.append('image_file', data.image_file);
      if (data.image_type) formData.append('image_type', data.image_type);
      formData.append('medical_record', recordId);

      const response = await apiClient.post(`/medical-records/medical-records/${recordId}/add_image/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['medicalRecord', variables.recordId] });
      queryClient.invalidateQueries({ queryKey: ['medicalImages'] });
    },
  });

  // Create medical image
  const createMedicalImage = useMutation({
    mutationFn: async (data: MedicalImage & { image_file?: File }) => {
      // If there's a file, use FormData
      if (data.image_file) {
        const formData = new FormData();
        formData.append('title', data.title);
        if (data.description) formData.append('description', data.description);
        formData.append('image_file', data.image_file);
        if (data.image_type) formData.append('image_type', data.image_type);
        formData.append('medical_record', data.medical_record);

        const response = await apiClient.post('/medical-records/medical-images/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        return response.data;
      } else {
        // Standard JSON request if no file
        const response = await apiClient.post('/medical-records/medical-images/', data);
        return response.data;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medicalImages'] });
      // We don't know which medical record this belongs to, so invalidate all
      queryClient.invalidateQueries({ queryKey: ['medicalRecords'] });
      queryClient.invalidateQueries({ queryKey: ['myMedicalRecords'] });
    },
  });

  // Update medical image
  const updateMedicalImage = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: MedicalImageUpdate }) => {
      const response = await apiClient.put(`/medical-records/medical-images/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['medicalImage', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['medicalImages'] });
    },
  });

  // Delete medical image
  const deleteMedicalImage = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/medical-records/medical-images/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medicalImages'] });
      // We don't know which medical record this belongs to, so invalidate all
      queryClient.invalidateQueries({ queryKey: ['medicalRecords'] });
      queryClient.invalidateQueries({ queryKey: ['myMedicalRecords'] });
    },
  });

  return {
    // Medical Records
    useAllMedicalRecords,
    useMyMedicalRecords,
    useMedicalRecord,
    createMedicalRecord,
    updateMedicalRecord,
    deleteMedicalRecord,

    // Access Logs
    useMedicalRecordAccessLogs,
    useAllAccessLogs,
    useAccessLog,

    // Medical Images
    useAllMedicalImages,
    useMedicalImage,
    addImageToMedicalRecord,
    createMedicalImage,
    updateMedicalImage,
    deleteMedicalImage,
  };
};
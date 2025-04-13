import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import {
  DoctorAvailability,
  DoctorProfile,
  DoctorTimeOff,
  DoctorWithUser,
  Specialization,
} from '@/types/api/doctors';

export const useDoctors = () => {
  const queryClient = useQueryClient();

  // Fetch all doctors
  const useDoctorsList = () => {
    return useQuery({
      queryKey: ['doctors'],
      queryFn: async () => {
        const response = await apiClient.get('/doctors/doctors/');
        return response.data;
      },
    });
  };

  // Fetch my doctor profile (for doctors)
  const useMyDoctorProfile = () => {
    return useQuery({
      queryKey: ['myDoctorProfile'],
      queryFn: async () => {
        const response = await apiClient.get('/doctors/doctors/me/');
        // The API returns an array with a single item
        return response.data[0];
      },
      enabled: !!localStorage.getItem('auth_token'),
    });
  };

  // Fetch single doctor
  const useDoctor = (id: string) => {
    return useQuery({
      queryKey: ['doctor', id],
      queryFn: async () => {
        const response = await apiClient.get(`/doctors/doctors/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  // Create doctor with user
  const createDoctor = useMutation({
    mutationFn: async (data: DoctorWithUser) => {
      const response = await apiClient.post('/doctors/doctors/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctors'] });
    },
  });

  // Update doctor profile
  const updateDoctor = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<DoctorProfile> }) => {
      const response = await apiClient.put(`/doctors/doctors/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['doctor', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['doctors'] });
      queryClient.invalidateQueries({ queryKey: ['myDoctorProfile'] });
    },
  });

  // Delete doctor
  const deleteDoctor = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/doctors/doctors/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctors'] });
    },
  });

  // Doctor Availabilities
  const useDoctorAvailabilities = (doctorId: string) => {
    return useQuery({
      queryKey: ['doctorAvailabilities', doctorId],
      queryFn: async () => {
        const response = await apiClient.get(`/doctors/doctors/${doctorId}/availabilities/`);
        return response.data;
      },
      enabled: !!doctorId,
    });
  };

  const useAllAvailabilities = () => {
    return useQuery({
      queryKey: ['allAvailabilities'],
      queryFn: async () => {
        const response = await apiClient.get('/doctors/doctor-availabilities/');
        return response.data;
      },
    });
  };

  const addDoctorAvailability = useMutation({
    mutationFn: async ({ doctorId, data }: { doctorId: string; data: DoctorAvailability }) => {
      const response = await apiClient.post(`/doctors/doctors/${doctorId}/add_availability/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['doctorAvailabilities', variables.doctorId] });
      queryClient.invalidateQueries({ queryKey: ['allAvailabilities'] });
      queryClient.invalidateQueries({ queryKey: ['doctor', variables.doctorId] });
    },
  });

  const createAvailability = useMutation({
    mutationFn: async (data: DoctorAvailability) => {
      const response = await apiClient.post('/doctors/doctor-availabilities/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allAvailabilities'] });
    },
  });

  const updateAvailability = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<DoctorAvailability> }) => {
      const response = await apiClient.put(`/doctors/doctor-availabilities/${id}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allAvailabilities'] });
      // Since we don't know which doctor this availability belongs to, invalidate all
      queryClient.invalidateQueries({ queryKey: ['doctorAvailabilities'] });
    },
  });

  const deleteAvailability = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/doctors/doctor-availabilities/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allAvailabilities'] });
      queryClient.invalidateQueries({ queryKey: ['doctorAvailabilities'] });
    },
  });

  // Doctor Time Offs
  const useDoctorTimeOffs = (doctorId: string) => {
    return useQuery({
      queryKey: ['doctorTimeOffs', doctorId],
      queryFn: async () => {
        const response = await apiClient.get(`/doctors/doctors/${doctorId}/time_offs/`);
        return response.data;
      },
      enabled: !!doctorId,
    });
  };

  const useAllTimeOffs = () => {
    return useQuery({
      queryKey: ['allTimeOffs'],
      queryFn: async () => {
        const response = await apiClient.get('/doctors/doctor-time-offs/');
        return response.data;
      },
    });
  };

  const addDoctorTimeOff = useMutation({
    mutationFn: async ({ doctorId, data }: { doctorId: string; data: DoctorTimeOff }) => {
      const response = await apiClient.post(`/doctors/doctors/${doctorId}/add_time_off/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['doctorTimeOffs', variables.doctorId] });
      queryClient.invalidateQueries({ queryKey: ['allTimeOffs'] });
      queryClient.invalidateQueries({ queryKey: ['doctor', variables.doctorId] });
    },
  });

  const createTimeOff = useMutation({
    mutationFn: async (data: DoctorTimeOff) => {
      const response = await apiClient.post('/doctors/doctor-time-offs/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allTimeOffs'] });
    },
  });

  const updateTimeOff = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<DoctorTimeOff> }) => {
      const response = await apiClient.put(`/doctors/doctor-time-offs/${id}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allTimeOffs'] });
      queryClient.invalidateQueries({ queryKey: ['doctorTimeOffs'] });
    },
  });

  const deleteTimeOff = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/doctors/doctor-time-offs/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allTimeOffs'] });
      queryClient.invalidateQueries({ queryKey: ['doctorTimeOffs'] });
    },
  });

  // Doctor Available Slots
  const useDoctorAvailableSlots = (doctorId: string, date?: string) => {
    return useQuery({
      queryKey: ['doctorAvailableSlots', doctorId, date],
      queryFn: async () => {
        let url = `/doctors/doctors/${doctorId}/available_slots/`;
        if (date) {
          url += `?date=${date}`;
        }
        const response = await apiClient.get(url);
        return response.data;
      },
      enabled: !!doctorId,
    });
  };

  // Specializations
  const useSpecializations = () => {
    return useQuery({
      queryKey: ['specializations'],
      queryFn: async () => {
        const response = await apiClient.get('/doctors/specializations/');
        return response.data;
      },
    });
  };

  const useSpecialization = (id: string) => {
    return useQuery({
      queryKey: ['specialization', id],
      queryFn: async () => {
        const response = await apiClient.get(`/doctors/specializations/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  const createSpecialization = useMutation({
    mutationFn: async (data: Specialization) => {
      const response = await apiClient.post('/doctors/specializations/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['specializations'] });
    },
  });

  const updateSpecialization = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Specialization> }) => {
      const response = await apiClient.put(`/doctors/specializations/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['specialization', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['specializations'] });
    },
  });

  const deleteSpecialization = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/doctors/specializations/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['specializations'] });
    },
  });

  return {
    // Doctors
    useDoctorsList,
    useMyDoctorProfile,
    useDoctor,
    createDoctor,
    updateDoctor,
    deleteDoctor,

    // Availabilities
    useDoctorAvailabilities,
    useAllAvailabilities,
    addDoctorAvailability,
    createAvailability,
    updateAvailability,
    deleteAvailability,

    // Time Offs
    useDoctorTimeOffs,
    useAllTimeOffs,
    addDoctorTimeOff,
    createTimeOff,
    updateTimeOff,
    deleteTimeOff,

    // Available Slots
    useDoctorAvailableSlots,

    // Specializations
    useSpecializations,
    useSpecialization,
    createSpecialization,
    updateSpecialization,
    deleteSpecialization,
  };
};
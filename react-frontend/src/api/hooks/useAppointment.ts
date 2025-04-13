import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import {
  // Appointment,
  AppointmentCreate,
  AppointmentReschedule,
  AppointmentReminder,
  AppointmentType,
  AppointmentUpdate,
} from '@/types/api/appointments';

export const useAppointments = () => {
  const queryClient = useQueryClient();

  // Fetch all appointments
  const useAllAppointments = () => {
    return useQuery({
      queryKey: ['appointments'],
      queryFn: async () => {
        const response = await apiClient.get('/appointments/appointments/');
        return response.data;
      },
    });
  };

  // Fetch my appointments (for patients)
  const useMyAppointments = () => {
    return useQuery({
      queryKey: ['myAppointments'],
      queryFn: async () => {
        const response = await apiClient.get('/appointments/appointments/my_appointments/');
        return response.data;
      },
    });
  };

  // Fetch doctor schedule (for doctors)
  const useDoctorSchedule = () => {
    return useQuery({
      queryKey: ['doctorSchedule'],
      queryFn: async () => {
        const response = await apiClient.get('/appointments/appointments/doctor_schedule/');
        return response.data;
      },
    });
  };

  // Fetch single appointment
  const useAppointment = (id: string) => {
    return useQuery({
      queryKey: ['appointment', id],
      queryFn: async () => {
        const response = await apiClient.get(`/appointments/appointments/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  // Create appointment
  const createAppointment = useMutation({
    mutationFn: async (appointment: AppointmentCreate) => {
      const response = await apiClient.post('/appointments/appointments/', appointment);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['myAppointments'] });
      queryClient.invalidateQueries({ queryKey: ['doctorSchedule'] });
    },
  });

  // Update appointment
  const updateAppointment = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: AppointmentUpdate }) => {
      const response = await apiClient.put(`/appointments/appointments/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['appointment', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['myAppointments'] });
      queryClient.invalidateQueries({ queryKey: ['doctorSchedule'] });
    },
  });

  // Reschedule appointment
  const rescheduleAppointment = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: AppointmentReschedule }) => {
      const response = await apiClient.post(`/appointments/appointments/${id}/reschedule/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['appointment', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['myAppointments'] });
      queryClient.invalidateQueries({ queryKey: ['doctorSchedule'] });
    },
  });

  // Cancel appointment (implemented as update with status=CANCELLED)
  const cancelAppointment = useMutation({
    mutationFn: async (id: string) => {
      const appointment = await apiClient.get(`/appointments/appointments/${id}/`);
      const updatedData = { ...appointment.data, status: 'CANCELLED' };
      const response = await apiClient.put(`/appointments/appointments/${id}/`, updatedData);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['appointment', id] });
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['myAppointments'] });
      queryClient.invalidateQueries({ queryKey: ['doctorSchedule'] });
    },
  });

  // Delete appointment
  const deleteAppointment = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/appointments/appointments/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['myAppointments'] });
      queryClient.invalidateQueries({ queryKey: ['doctorSchedule'] });
    },
  });

  // Appointment Types
  const useAppointmentTypes = () => {
    return useQuery({
      queryKey: ['appointmentTypes'],
      queryFn: async () => {
        const response = await apiClient.get('/appointments/appointment-types/');
        return response.data;
      },
    });
  };

  const useAppointmentType = (id: string) => {
    return useQuery({
      queryKey: ['appointmentType', id],
      queryFn: async () => {
        const response = await apiClient.get(`/appointments/appointment-types/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  const createAppointmentType = useMutation({
    mutationFn: async (data: AppointmentType) => {
      const response = await apiClient.post('/appointments/appointment-types/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointmentTypes'] });
    },
  });

  const updateAppointmentType = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: AppointmentType }) => {
      const response = await apiClient.put(`/appointments/appointment-types/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['appointmentType', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['appointmentTypes'] });
    },
  });

  const deleteAppointmentType = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/appointments/appointment-types/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointmentTypes'] });
    },
  });

  // Appointment Reminders
  const useAppointmentReminders = () => {
    return useQuery({
      queryKey: ['appointmentReminders'],
      queryFn: async () => {
        const response = await apiClient.get('/appointments/appointment-reminders/');
        return response.data;
      },
    });
  };

  const useAppointmentReminder = (id: string) => {
    return useQuery({
      queryKey: ['appointmentReminder', id],
      queryFn: async () => {
        const response = await apiClient.get(`/appointments/appointment-reminders/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  const createAppointmentReminder = useMutation({
    mutationFn: async (data: AppointmentReminder) => {
      const response = await apiClient.post('/appointments/appointment-reminders/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointmentReminders'] });
    },
  });

  const updateAppointmentReminder = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: AppointmentReminder }) => {
      const response = await apiClient.put(`/appointments/appointment-reminders/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['appointmentReminder', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['appointmentReminders'] });
    },
  });

  const deleteAppointmentReminder = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/appointments/appointment-reminders/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointmentReminders'] });
    },
  });

  return {
    // Appointments
    useAllAppointments,
    useMyAppointments,
    useDoctorSchedule,
    useAppointment,
    createAppointment,
    updateAppointment,
    rescheduleAppointment,
    cancelAppointment,
    deleteAppointment,

    // Appointment Types
    useAppointmentTypes,
    useAppointmentType,
    createAppointmentType,
    updateAppointmentType,
    deleteAppointmentType,

    // Appointment Reminders
    useAppointmentReminders,
    useAppointmentReminder,
    createAppointmentReminder,
    updateAppointmentReminder,
    deleteAppointmentReminder,
  };
};
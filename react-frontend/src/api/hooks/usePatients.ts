import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import {
  PatientProfile,
  PatientWithUser,
  InsuranceProvider,
  PatientInsurance,
  // AddInsuranceRequest,
} from '@/types/api/patients';

export const usePatients = () => {
  const queryClient = useQueryClient();

  // Fetch all patients
  const useAllPatients = () => {
    return useQuery({
      queryKey: ['patients'],
      queryFn: async () => {
        const response = await apiClient.get('/patients/patients/');
        return response.data;
      },
    });
  };

  // Fetch my patient profile (for patients)
  const useMyPatientProfile = () => {
    return useQuery({
      queryKey: ['myPatientProfile'],
      queryFn: async () => {
        const response = await apiClient.get('/patients/patients/me/');
        return response.data[0];
      },
      enabled: !!localStorage.getItem('auth_token'),
    });
  };

  // Fetch single patient
  const usePatient = (id: string) => {
    return useQuery({
      queryKey: ['patient', id],
      queryFn: async () => {
        const response = await apiClient.get(`/patients/patients/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  // Create patient with user
  const createPatient = useMutation({
    mutationFn: async (data: PatientWithUser) => {
      const response = await apiClient.post('/patients/patients/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });

  // Update patient profile
  const updatePatient = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<PatientProfile> }) => {
      const response = await apiClient.put(`/patients/patients/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['patient', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['patients'] });
      queryClient.invalidateQueries({ queryKey: ['myPatientProfile'] });
    },
  });

  // Delete patient
  const deletePatient = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/patients/patients/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });

  // Patient Insurances
  const usePatientInsurances = (patientId: string) => {
    return useQuery({
      queryKey: ['patientInsurances', patientId],
      queryFn: async () => {
        const response = await apiClient.get(`/patients/patients/${patientId}/insurances/`);
        return response.data;
      },
      enabled: !!patientId,
    });
  };

  const useAllPatientInsurances = () => {
    return useQuery({
      queryKey: ['allPatientInsurances'],
      queryFn: async () => {
        const response = await apiClient.get('/patients/patient-insurances/');
        return response.data;
      },
    });
  };

  const usePatientInsurance = (id: string) => {
    return useQuery({
      queryKey: ['patientInsurance', id],
      queryFn: async () => {
        const response = await apiClient.get(`/patients/patient-insurances/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  const addPatientInsurance = useMutation({
    mutationFn: async ({ patientId, data }: { patientId: string; data: PatientInsurance }) => {
      const response = await apiClient.post(`/patients/patients/${patientId}/add_insurance/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['patientInsurances', variables.patientId] });
      queryClient.invalidateQueries({ queryKey: ['allPatientInsurances'] });
      queryClient.invalidateQueries({ queryKey: ['patient', variables.patientId] });
    },
  });

  const createPatientInsurance = useMutation({
    mutationFn: async (data: PatientInsurance) => {
      const response = await apiClient.post('/patients/patient-insurances/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allPatientInsurances'] });
    },
  });

  const updatePatientInsurance = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<PatientInsurance> }) => {
      const response = await apiClient.put(`/patients/patient-insurances/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['patientInsurance', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['allPatientInsurances'] });
      queryClient.invalidateQueries({ queryKey: ['patientInsurances'] });
    },
  });

  const deletePatientInsurance = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/patients/patient-insurances/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allPatientInsurances'] });
      queryClient.invalidateQueries({ queryKey: ['patientInsurances'] });
    },
  });

  // Insurance Providers
  const useInsuranceProviders = () => {
    return useQuery({
      queryKey: ['insuranceProviders'],
      queryFn: async () => {
        const response = await apiClient.get('/patients/insurance-providers/');
        return response.data;
      },
    });
  };

  const useInsuranceProvider = (id: string) => {
    return useQuery({
      queryKey: ['insuranceProvider', id],
      queryFn: async () => {
        const response = await apiClient.get(`/patients/insurance-providers/${id}/`);
        return response.data;
      },
      enabled: !!id,
    });
  };

  const createInsuranceProvider = useMutation({
    mutationFn: async (data: InsuranceProvider) => {
      const response = await apiClient.post('/patients/insurance-providers/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['insuranceProviders'] });
    },
  });

  const updateInsuranceProvider = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<InsuranceProvider> }) => {
      const response = await apiClient.put(`/patients/insurance-providers/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['insuranceProvider', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['insuranceProviders'] });
    },
  });

  const deleteInsuranceProvider = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/patients/insurance-providers/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['insuranceProviders'] });
    },
  });

  return {
    // Patients
    useAllPatients,
    useMyPatientProfile,
    usePatient,
    createPatient,
    updatePatient,
    deletePatient,

    // Patient Insurances
    usePatientInsurances,
    useAllPatientInsurances,
    usePatientInsurance,
    addPatientInsurance,
    createPatientInsurance,
    updatePatientInsurance,
    deletePatientInsurance,

    // Insurance Providers
    useInsuranceProviders,
    useInsuranceProvider,
    createInsuranceProvider,
    updateInsuranceProvider,
    deleteInsuranceProvider,
  };
};
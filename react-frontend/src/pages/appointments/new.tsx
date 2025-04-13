import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import AppointmentForm from '@/components/appointments/AppointmentForm';
import PageLayout from '@/components/layout/PageLayout';
import { addAppointment } from '@/data/mockData';
import { toast } from 'sonner';
import { Appointment } from '@/types';

const NewAppointmentPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialPatientId = searchParams.get('patientId') || '';
  const initialDoctorId = searchParams.get('doctorId') || '';

  const handleSubmit = (formData: Omit<Appointment, 'id' | 'status'>) => {
    setIsLoading(true);

    try {
      // Add a small delay to simulate API call
      setTimeout(() => {
        // Add status as 'scheduled' by default for new appointments
        const appointmentData = {
          ...formData,
          status: 'scheduled' as const
        };

        const result = addAppointment(appointmentData);

        if ('error' in result) {
          toast.error(result.error);
          setIsLoading(false);
          return;
        }

        toast.success(`Appointment scheduled for ${formData.date} at ${formData.startTime}`);

        navigate('/appointments');
      }, 1000);
    } catch (error) {
      toast.error("Failed to create appointment. Please try again.");
      console.error('Error creating new appointment', error)
      setIsLoading(false);
    }
  };

  const initialData = {
    patientId: initialPatientId,
    doctorId: initialDoctorId,
    date: '',
    startTime: '',
    endTime: '', // Adding the missing endTime property
    notes: '',
  };

  return (
    <PageLayout>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Schedule New Appointment</h1>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <AppointmentForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            initialData={initialData}
          />
        </div>
      </div>
    </PageLayout>
  );
};

export default NewAppointmentPage;
export type Patient = {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  address: string;
  insuranceProvider?: string;
  insuranceId?: string;
  medicalHistory?: string;
};

export type Doctor = {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  specialization: string;
  qualifications: string;
  availability: Availability[];
};

export type Availability = {
  day: string;
  startTime: string;
  endTime: string;
};

export type AppointmentStatus = 'scheduled' | 'completed' | 'cancelled';

export type Appointment = {
  id: string;
  patientId: string;
  doctorId: string;
  date: string;
  startTime: string;
  endTime: string;
  status: AppointmentStatus;
  notes?: string;
};
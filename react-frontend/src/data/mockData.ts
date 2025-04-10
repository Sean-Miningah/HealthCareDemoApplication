import { Patient, Doctor, Appointment, AppointmentStatus } from '@/types';
import { v4 as uuidv4 } from 'uuid';

// Mock Patients
export const patients: Patient[] = [
  {
    id: '1',
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '(555) 123-4567',
    dateOfBirth: '1985-05-15',
    address: '123 Main St, Anytown, USA',
    insuranceProvider: 'Health Plus',
    insuranceId: 'HP12345678',
    medicalHistory: 'Hypertension, Asthma',
  },
  {
    id: '2',
    firstName: 'Jane',
    lastName: 'Smith',
    email: 'jane.smith@example.com',
    phone: '(555) 987-6543',
    dateOfBirth: '1990-09-20',
    address: '456 Oak Ave, Somecity, USA',
    insuranceProvider: 'MediCare',
    insuranceId: 'MC87654321',
    medicalHistory: 'Allergies, Diabetes Type 2',
  },
  {
    id: '3',
    firstName: 'Robert',
    lastName: 'Johnson',
    email: 'robert.j@example.com',
    phone: '(555) 456-7890',
    dateOfBirth: '1978-12-10',
    address: '789 Pine Rd, Othertown, USA',
    insuranceProvider: 'Blue Cross',
    insuranceId: 'BC45678901',
    medicalHistory: 'Arthritis',
  },
];

// Mock Doctors
export const doctors: Doctor[] = [
  {
    id: '1',
    firstName: 'Elizabeth',
    lastName: 'Chen',
    email: 'dr.chen@example.com',
    phone: '(555) 234-5678',
    specialization: 'Cardiology',
    qualifications: 'MD, PhD, FACC',
    availability: [
      { day: 'Monday', startTime: '09:00', endTime: '17:00' },
      { day: 'Wednesday', startTime: '09:00', endTime: '17:00' },
      { day: 'Friday', startTime: '09:00', endTime: '13:00' },
    ],
  },
  {
    id: '2',
    firstName: 'Michael',
    lastName: 'Rodriguez',
    email: 'dr.rodriguez@example.com',
    phone: '(555) 345-6789',
    specialization: 'Pediatrics',
    qualifications: 'MD, FAAP',
    availability: [
      { day: 'Monday', startTime: '10:00', endTime: '18:00' },
      { day: 'Tuesday', startTime: '10:00', endTime: '18:00' },
      { day: 'Thursday', startTime: '10:00', endTime: '18:00' },
    ],
  },
  {
    id: '3',
    firstName: 'Sarah',
    lastName: 'Johnson',
    email: 'dr.johnson@example.com',
    phone: '(555) 456-7890',
    specialization: 'Dermatology',
    qualifications: 'MD, FAAD',
    availability: [
      { day: 'Tuesday', startTime: '09:00', endTime: '17:00' },
      { day: 'Thursday', startTime: '09:00', endTime: '17:00' },
      { day: 'Friday', startTime: '14:00', endTime: '18:00' },
    ],
  },
];

// Mock Appointments
export const appointments: Appointment[] = [
  {
    id: '1',
    patientId: '1',
    doctorId: '1',
    date: '2025-04-07', // Monday
    startTime: '10:00',
    endTime: '10:30',
    status: 'scheduled',
    notes: 'Annual checkup',
  },
  {
    id: '2',
    patientId: '2',
    doctorId: '2',
    date: '2025-04-08', // Tuesday
    startTime: '11:00',
    endTime: '11:30',
    status: 'scheduled',
    notes: 'Follow-up appointment',
  },
  {
    id: '3',
    patientId: '3',
    doctorId: '3',
    date: '2025-04-10', // Thursday
    startTime: '14:00',
    endTime: '14:30',
    status: 'scheduled',
    notes: 'Initial consultation',
  },
];

// Helper Functions
export const addPatient = (patient: Omit<Patient, 'id'>): Patient => {
  const newPatient = { ...patient, id: uuidv4() };
  patients.push(newPatient);
  return newPatient;
};

export const addDoctor = (doctor: Omit<Doctor, 'id'>): Doctor => {
  const newDoctor = { ...doctor, id: uuidv4() };
  doctors.push(newDoctor);
  return newDoctor;
};

export const addAppointment = (appointment: Omit<Appointment, 'id'>): Appointment | { error: string } => {
  // Check if doctor exists
  const doctor = doctors.find(d => d.id === appointment.doctorId);
  if (!doctor) {
    return { error: 'Doctor not found' };
  }

  // Check if patient exists
  const patient = patients.find(p => p.id === appointment.patientId);
  if (!patient) {
    return { error: 'Patient not found' };
  }

  // Check if the doctor is available on that day
  const appointmentDate = new Date(appointment.date);
  const dayOfWeek = appointmentDate.toLocaleDateString('en-US', { weekday: 'long' });

  const doctorAvailability = doctor.availability.find(a => a.day === dayOfWeek);
  if (!doctorAvailability) {
    return { error: `Doctor is not available on ${dayOfWeek}` };
  }

  // Check if the appointment time is within doctor's working hours
  if (appointment.startTime < doctorAvailability.startTime ||
      appointment.endTime > doctorAvailability.endTime) {
    return {
      error: `Doctor is only available from ${doctorAvailability.startTime} to ${doctorAvailability.endTime} on ${dayOfWeek}`
    };
  }

  // Check for conflicts with existing appointments
  const conflictingAppointment = appointments.find(a =>
    a.doctorId === appointment.doctorId &&
    a.date === appointment.date &&
    a.status !== 'cancelled' &&
    ((appointment.startTime >= a.startTime && appointment.startTime < a.endTime) ||
     (appointment.endTime > a.startTime && appointment.endTime <= a.endTime) ||
     (appointment.startTime <= a.startTime && appointment.endTime >= a.endTime))
  );

  if (conflictingAppointment) {
    return { error: 'This time slot is already booked' };
  }

  const newAppointment = { ...appointment, id: uuidv4() };
  appointments.push(newAppointment);
  return newAppointment;
};

export const updateAppointmentStatus = (id: string, status: AppointmentStatus): Appointment | { error: string } => {
  const appointmentIndex = appointments.findIndex(a => a.id === id);
  if (appointmentIndex === -1) {
    return { error: 'Appointment not found' };
  }

  appointments[appointmentIndex].status = status;
  return appointments[appointmentIndex];
};

export const getPatientAppointments = (patientId: string): Appointment[] => {
  return appointments.filter(a => a.patientId === patientId);
};

export const getDoctorAppointments = (doctorId: string): Appointment[] => {
  return appointments.filter(a => a.doctorId === doctorId);
};

export const getAppointmentDetails = (appointmentId: string): { appointment: Appointment, doctor: Doctor, patient: Patient } | { error: string } => {
  const appointment = appointments.find(a => a.id === appointmentId);
  if (!appointment) {
    return { error: 'Appointment not found' };
  }

  const doctor = doctors.find(d => d.id === appointment.doctorId);
  if (!doctor) {
    return { error: 'Doctor not found' };
  }

  const patient = patients.find(p => p.id === appointment.patientId);
  if (!patient) {
    return { error: 'Patient not found' };
  }

  return { appointment, doctor, patient };
};
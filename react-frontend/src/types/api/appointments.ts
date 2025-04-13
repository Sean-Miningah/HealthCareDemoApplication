export type ReminderType = 'EMAIL' | 'SMS' | 'BOTH';
export type AppointmentStatus =
  'SCHEDULED' | 'CONFIRMED' | 'CHECKED_IN' |
  'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' |
  'NO_SHOW' | 'RESCHEDULED';

export interface AppointmentReminder {
  id?: string;
  reminder_type?: ReminderType;
  scheduled_time: string;
  message?: string;
  sent?: boolean;
  sent_time?: string;
  appointment: string;
}

export interface AppointmentType {
  id?: string;
  name: string;
  description?: string;
  duration_minutes?: number;
  color_hex?: string;
}

export interface Appointment {
  id?: string;
  patient: string;
  patient_name?: string;
  doctor: string;
  doctor_name?: string;
  appointment_type: string;
  appointment_type_name?: string;
  start_datetime: string;
  end_datetime: string;
  status?: AppointmentStatus;
  reason?: string;
  notes?: string;
  is_virtual?: boolean;
  meeting_link?: string;
  original_appointment?: string;
  reminders?: AppointmentReminder[];
  created_at?: string;
  updated_at?: string;
}

export interface AppointmentCreate extends Appointment {
  create_reminder?: boolean;
  reminder_hours_before?: number;
  reminder_type?: ReminderType;
}

export type AppointmentUpdate = Appointment

export interface AppointmentReschedule {
  new_start_datetime: string;
  reason?: string;
}
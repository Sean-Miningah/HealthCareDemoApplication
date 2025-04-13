import type { User } from "./accounts";


export type DayOfWeek = 0 | 1 | 2 | 3 | 4 | 5 | 6;

export interface DoctorAvailability {
  id?: string;
  day_of_week: DayOfWeek;
  day_name?: string;
  start_time: string;
  end_time: string;
}

export interface DoctorTimeOff {
  id?: string;
  start_datetime: string;
  end_datetime: string;
  reason?: string;
}

export interface Specialization {
  id?: string;
  name: string;
  description?: string;
}

export interface DoctorProfile {
  id?: string;
  user?: string;
  user_email?: string;
  user_full_name?: string;
  license_number: string;
  specializations?: Specialization[];
  years_of_experience?: number;
  biography?: string;
  education?: string;
  accepting_new_patients?: boolean;
  consultation_fee?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  availabilities?: DoctorAvailability[];
}

export interface DoctorWithUser {
  user: User;
  license_number: string;
  specialization_ids: string[];
  years_of_experience?: number;
  biography?: string;
  education?: string;
  accepting_new_patients?: boolean;
  consultation_fee?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  availabilities?: DoctorAvailability[];
}

export interface AvailabilityRequest {
  availabilities: DoctorAvailability[];
}

export interface TimeOffRequest {
  time_offs: DoctorTimeOff[];
}
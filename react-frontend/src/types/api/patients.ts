import type { User } from './accounts.ts'

export type Gender = 'M' | 'F' | 'O';
export type BloodType = 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | 'O+' | 'O-';

export interface InsuranceProvider {
  id?: string;
  name: string;
  contact_number?: string;
  contact_email?: string;
}

export interface PatientInsurance {
  id?: string;
  insurance_provider: string;
  insurance_provider_name?: string;
  policy_number: string;
  group_number?: string;
  policy_holder_name: string;
  policy_holder_relation?: string;
  start_date: string;
  end_date?: string;
  is_primary?: boolean;
}

export interface PatientProfile {
  id?: string;
  user?: string;
  user_email?: string;
  user_full_name?: string;
  date_of_birth?: string;
  gender?: Gender;
  blood_type?: BloodType;
  allergies?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
  medical_conditions?: string;
  current_medications?: string;
  insurances?: PatientInsurance[];
}

export interface PatientWithUser {
  user: User;
  date_of_birth?: string;
  gender?: Gender;
  blood_type?: BloodType;
  allergies?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
  medical_conditions?: string;
  current_medications?: string;
  insurances?: PatientInsurance[];
}

export interface AddInsuranceRequest {
  insurance: PatientInsurance;
}
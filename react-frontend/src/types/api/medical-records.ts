export interface MedicalRecordAccess {
  id?: string;
  user?: string;
  user_email?: string;
  user_name?: string;
  accessed_at?: string;
  access_reason: string;
  ip_address?: string;
}

export interface MedicalImage {
  id?: string;
  title: string;
  description?: string;
  image_file?: string;
  image_type?: string;
  created_at?: string;
  medical_record: string;
}

export interface MedicalImageUpdate {
  id?: string;
  title: string;
  description?: string;
  image_type?: string;
}

export interface MedicalRecord {
  id?: string;
  patient: string;
  patient_name?: string;
  doctor: string;
  doctor_name?: string;
  appointment?: string;
  appointment_date?: string;
  diagnosis?: string;
  treatment_plan?: string;
  prescription?: string;
  notes?: string;
  temperature?: string;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  pulse_rate?: number;
  respiratory_rate?: number;
  weight?: string;
  height?: string;
  is_confidential?: boolean;
  images?: MedicalImage[];
  created_at?: string;
  updated_at?: string;
}

export interface MedicalRecordCreate extends MedicalRecord {
  images?: MedicalImage[];
}

export type MedicalRecordUpdate = MedicalRecord

export interface AddImageRequest {
  title: string;
  description?: string;
  image_file: File;
  image_type?: string;
}
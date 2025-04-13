export type UserRole = 'ADMIN' | 'DOCTOR' | 'PATIENT' | 'STAFF';

export interface EmailAuthToken {
  email: string;
  password: string;
}

export interface User {
  id?: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  role?: UserRole;
  password: string;
  password_confirmation: string;
  created_at?: string;
}

export interface UserUpdateRequest {
  email?: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
}

export interface ChangePasswordRequest {
  password: string;
  password_confirmation: string;
  current_password?: string;
}

export interface ResetPasswordRequest {
  email: string;
}

export interface ResetPasswordConfirmRequest {
  token: string;
  password: string;
  password_confirmation: string;
}
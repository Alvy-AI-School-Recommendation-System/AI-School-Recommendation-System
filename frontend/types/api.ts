/**
 * API response type definitions
 */

export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: string
}

export interface ProfileResponse {
  id: number
  email: string
  username?: string
  nickname?: string
  avatar_url?: string
  bio?: string
  phone?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface ProfileUpdateRequest {
  username?: string
  nickname?: string
  avatar_url?: string
  bio?: string
  phone?: string
}

export interface PasswordChangeRequest {
  old_password: string
  new_password: string
}


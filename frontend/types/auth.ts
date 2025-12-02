/**
 * Authentication-related type definitions
 */

export interface User {
  id: number
  email: string
  username?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface GoogleLoginRequest {
  id_token: string
}

export interface TokenRefreshRequest {
  refresh_token: string
}


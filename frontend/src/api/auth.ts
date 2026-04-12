import { apiFetch } from './client'

export interface User {
  id: string
  name: string
  email: string
}

export async function getMe(): Promise<User> {
  return apiFetch<User>('/auth/me')
}

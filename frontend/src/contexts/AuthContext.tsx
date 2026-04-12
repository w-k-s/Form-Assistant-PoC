import { createContext, useContext } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getMe, type User } from '../api/auth'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: user = null, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
    retry: false,
    staleTime: Infinity,
  })

  return (
    <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}

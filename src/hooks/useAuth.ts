import { useKV } from '@github/spark/hooks'
import { User, Permission, ROLE_PERMISSIONS } from '@/types'
import { useEffect } from 'react'

export function useAuth() {
  const [currentUser, setCurrentUser] = useKV<User | null>('current-user', null)
  const [users, setUsers] = useKV<User[]>('system-users', [])

  // Debug useKV values
  useEffect(() => {
    console.log('useAuth state update:')
    console.log('  currentUser:', currentUser?.username)
    console.log('  users count:', users?.length)
  }, [currentUser, users])

  const login = (user: User) => {
    console.log('Login called for:', user.username)
    
    const updatedUser = {
      ...user,
      lastLogin: new Date().toISOString(),
      permissions: user.permissions || ROLE_PERMISSIONS[user.role] || []
    }
    
    console.log('Setting currentUser to:', updatedUser.username)
    setCurrentUser(updatedUser)
    
    // Update in users list
    setUsers(current => 
      (current || []).map(u => 
        u.id === user.id ? updatedUser : u
      )
    )
  }

  const hasPermission = (permission: Permission): boolean => {
    if (!currentUser) return false
    if (currentUser.role === 'admin') return true
    return currentUser.permissions?.includes(permission) || false
  }

  const isAdmin = (): boolean => {
    return currentUser?.role === 'admin'
  }

  const canAccessModule = (permission: Permission): boolean => {
    return hasPermission(permission)
  }

  const logout = () => {
    console.log('Logging out user:', currentUser?.username)
    setCurrentUser(null)
  }

  const createUser = (userData: Omit<User, 'id' | 'createdAt' | 'permissions'>) => {
    const newUser: User = {
      ...userData,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      permissions: ROLE_PERMISSIONS[userData.role],
      createdBy: currentUser?.id
    }

    console.log('Creating user:', newUser.username, 'with permissions:', newUser.permissions.length)
    setUsers(current => [...(current || []), newUser])
    return newUser
  }

  const updateUser = (userId: string, updates: Partial<User>) => {
    setUsers(current => 
      (current || []).map(user => 
        user.id === userId 
          ? { 
              ...user, 
              ...updates,
              permissions: updates.role ? ROLE_PERMISSIONS[updates.role] : (updates.permissions || user.permissions)
            }
          : user
      )
    )

    if (currentUser?.id === userId) {
      const updatedCurrentUser = { 
        ...currentUser, 
        ...updates,
        permissions: updates.role ? ROLE_PERMISSIONS[updates.role] : (updates.permissions || currentUser.permissions)
      }
      setCurrentUser(updatedCurrentUser)
    }
  }

  const deleteUser = (userId: string) => {
    setUsers(current => (current || []).filter(user => user.id !== userId))
    
    if (currentUser?.id === userId) {
      logout()
    }
  }

  return {
    currentUser,
    users,
    hasPermission,
    isAdmin,
    canAccessModule,
    login,
    logout,
    createUser,
    updateUser,
    deleteUser
  }
}
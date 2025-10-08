import { useKV } from '@github/spark/hooks'
import { User, Permission, ROLE_PERMISSIONS } from '@/types'
import { useEffect } from 'react'

export function useAuth() {
  const [currentUser, setCurrentUser] = useKV<User | null>('current-user', null)
  const [users, setUsers] = useKV<User[]>('system-users', [])

  // Initialize with Elvio user if needed
  useEffect(() => {
    if (!users || users.length === 0) {
      const elvioAdmin: User = {
        id: 'elvio-admin-001',
        username: 'elvio',
        name: 'Elvio - Administrador Master',
        email: 'elvio@4mcontabilidade.com.br',
        role: 'admin',
        permissions: ROLE_PERMISSIONS.admin,
        isActive: true,
        createdAt: new Date().toISOString()
      }
      setUsers([elvioAdmin])
      console.log('Initialized Elvio admin user')
    }
  }, [users, setUsers])

  // Debug useKV values
  useEffect(() => {
    console.log('Sistema de autenticação carregado - usuários:', users?.length)
  }, [users])

  const login = (user: User) => {
    console.log('Fazendo login para:', user.username)
    
    const updatedUser = {
      ...user,
      lastLogin: new Date().toISOString(),
      permissions: user.permissions || ROLE_PERMISSIONS[user.role] || []
    }
    
    // Set current user with functional update
    setCurrentUser(() => {
      console.log('Usuário autenticado:', updatedUser.username)
      return updatedUser
    })
    
    // Update in users list if needed
    setUsers(current => {
      const currentUsers = current || []
      const userExists = currentUsers.find(u => u.id === user.id)
      
      if (userExists) {
        return currentUsers.map(u => 
          u.id === user.id ? updatedUser : u
        )
      } else {
        return [...currentUsers, updatedUser]
      }
    })
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
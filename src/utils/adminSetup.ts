import { User, ROLE_PERMISSIONS } from '@/types'

/**
 * Ensures Elvio has full admin access
 */
export function ensureElvioAdminAccess(users: User[]): User[] {
  return users.map(user => {
    if (user.username === 'elvio' && user.role === 'admin') {
      return {
        ...user,
        permissions: ROLE_PERMISSIONS.admin,
        role: 'admin',
        isActive: true
      }
    }
    return user
  })
}

/**
 * Validates if a user has all required admin permissions
 */
export function validateAdminPermissions(user: User): boolean {
  if (user.role !== 'admin') return false
  
  const requiredPermissions = ROLE_PERMISSIONS.admin
  const userPermissions = user.permissions || []
  
  return requiredPermissions.every(permission => 
    userPermissions.includes(permission)
  )
}

/**
 * Fixes admin user permissions
 */
export function fixAdminPermissions(user: User): User {
  if (user.role === 'admin') {
    return {
      ...user,
      permissions: ROLE_PERMISSIONS.admin,
      isActive: true
    }
  }
  return user
}
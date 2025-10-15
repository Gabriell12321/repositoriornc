import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/hooks/useAuth'
import { ROLE_PERMISSIONS } from '@/types'

export default function DebugInfo() {
  const { currentUser, users } = useAuth()

  if (!currentUser) return null

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="text-sm">Debug - Informações do Usuário Atual</CardTitle>
      </CardHeader>
      <CardContent className="text-xs space-y-2">
        <div>
          <strong>Usuário:</strong> {currentUser.name} (@{currentUser.username})
        </div>
        <div>
          <strong>Função:</strong> <Badge className="text-xs">{currentUser.role}</Badge>
        </div>
        <div>
          <strong>Status:</strong> <Badge className={currentUser.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
            {currentUser.isActive ? 'Ativo' : 'Inativo'}
          </Badge>
        </div>
        <div>
          <strong>Permissões Atuais ({currentUser.permissions?.length || 0}):</strong>
          <div className="mt-1 flex flex-wrap gap-1">
            {currentUser.permissions?.map(permission => (
              <Badge key={permission} variant="outline" className="text-xs">
                {permission}
              </Badge>
            ))}
          </div>
        </div>
        <div>
          <strong>Permissões Esperadas para {currentUser.role} ({ROLE_PERMISSIONS[currentUser.role]?.length || 0}):</strong>
          <div className="mt-1 flex flex-wrap gap-1">
            {ROLE_PERMISSIONS[currentUser.role]?.map(permission => (
              <Badge 
                key={permission} 
                variant="outline" 
                className={`text-xs ${
                  currentUser.permissions?.includes(permission) 
                    ? 'bg-green-50 text-green-700' 
                    : 'bg-red-50 text-red-700'
                }`}
              >
                {permission}
              </Badge>
            ))}
          </div>
        </div>
        <div>
          <strong>Total de usuários no sistema:</strong> {users?.length || 0}
        </div>
      </CardContent>
    </Card>
  )
}
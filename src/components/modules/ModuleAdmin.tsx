import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useAuth } from '@/hooks/useAuth'
import { User, UserRole, ROLE_PERMISSIONS } from '@/types'
import { toast } from 'sonner'
import DebugInfo from '@/components/DebugInfo'
import { 
  Users, 
  Plus, 
  Pencil, 
  Trash, 
  Shield,
  UserCheck,
  Clock,
  Envelope,
  Key,
  Wrench
} from '@phosphor-icons/react'

export default function ModuleAdmin() {
  const { users, currentUser, createUser, updateUser, deleteUser, isAdmin } = useAuth()
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [formData, setFormData] = useState({
    username: '',
    name: '',
    email: '',
    role: 'recepcao' as UserRole
  })

  // Only admin can access this module
  if (!isAdmin()) {
    return (
      <div className="p-6 text-center">
        <Shield size={48} className="mx-auto mb-4 text-muted-foreground" />
        <h2 className="text-xl font-semibold mb-2">Acesso Negado</h2>
        <p className="text-muted-foreground">Você não tem permissão para acessar este módulo.</p>
      </div>
    )
  }

  const handleCreateUser = () => {
    if (!formData.username || !formData.name || !formData.email) {
      toast.error('Por favor, preencha todos os campos obrigatórios')
      return
    }

    // Check if username already exists
    if ((users || []).some(u => u.username.toLowerCase() === formData.username.toLowerCase())) {
      toast.error('Nome de usuário já existe')
      return
    }

    try {
      createUser({
        username: formData.username,
        name: formData.name,
        email: formData.email,
        role: formData.role,
        isActive: true
      })

      toast.success(`Usuário ${formData.name} criado com sucesso! Senha: ${formData.username}123`)
      
      // Reset form
      setFormData({
        username: '',
        name: '',
        email: '',
        role: 'recepcao'
      })
      setShowCreateDialog(false)
    } catch (error) {
      toast.error('Erro ao criar usuário')
    }
  }

  const handleUpdateUser = () => {
    if (!editingUser || !formData.name || !formData.email) {
      toast.error('Por favor, preencha todos os campos obrigatórios')
      return
    }

    try {
      updateUser(editingUser.id, {
        name: formData.name,
        email: formData.email,
        role: formData.role
      })

      toast.success('Usuário atualizado com sucesso!')
      
      setEditingUser(null)
      setFormData({
        username: '',
        name: '',
        email: '',
        role: 'recepcao'
      })
      setShowCreateDialog(false)
    } catch (error) {
      toast.error('Erro ao atualizar usuário')
    }
  }

  const handleDeleteUser = (user: User) => {
    if (user.id === currentUser?.id) {
      toast.error('Você não pode deletar sua própria conta')
      return
    }

    if (confirm(`Tem certeza que deseja excluir o usuário ${user.name}?`)) {
      deleteUser(user.id)
      toast.success('Usuário excluído com sucesso!')
    }
  }

  const handleEditUser = (user: User) => {
    setEditingUser(user)
    setFormData({
      username: user.username,
      name: user.name,
      email: user.email,
      role: user.role
    })
    setShowCreateDialog(true)
  }

  const toggleUserStatus = (user: User) => {
    if (user.id === currentUser?.id) {
      toast.error('Você não pode desativar sua própria conta')
      return
    }

    updateUser(user.id, { isActive: !user.isActive })
    toast.success(`Usuário ${user.isActive ? 'desativado' : 'ativado'} com sucesso!`)
  }

  const fixAdminPermissions = () => {
    if (!currentUser) return
    
    const adminUsers = (users || []).filter(u => u.role === 'admin')
    adminUsers.forEach(user => {
      console.log('Fixing permissions for admin:', user.username)
      updateUser(user.id, {
        permissions: ROLE_PERMISSIONS.admin,
        role: 'admin',
        isActive: true
      })
    })
    
    toast.success('Permissões de administradores atualizadas!')
  }

  const resetElvioAdmin = () => {
    const elvio = (users || []).find(u => u.username === 'elvio')
    if (elvio) {
      updateUser(elvio.id, {
        name: 'Elvio - Administrador',
        permissions: ROLE_PERMISSIONS.admin,
        role: 'admin',
        isActive: true,
        email: 'elvio@4mcontabilidade.com.br'
      })
      toast.success('Elvio resetado como administrador master!')
    } else {
      toast.error('Usuário Elvio não encontrado!')
    }
  }

  const getRoleLabel = (role: UserRole): string => {
    const labels = {
      admin: 'Administrador',
      fiscal: 'Fiscal',
      financeiro: 'Financeiro',
      contabil: 'Contábil',
      rh: 'Recursos Humanos',
      gerencial: 'Gerencial',
      recepcao: 'Recepção',
      readonly: 'Somente Leitura'
    }
    return labels[role]
  }

  const getRoleColor = (role: UserRole): string => {
    const colors = {
      admin: 'bg-red-100 text-red-800',
      fiscal: 'bg-blue-100 text-blue-800',
      financeiro: 'bg-green-100 text-green-800',
      contabil: 'bg-purple-100 text-purple-800',
      rh: 'bg-orange-100 text-orange-800',
      gerencial: 'bg-indigo-100 text-indigo-800',
      recepcao: 'bg-cyan-100 text-cyan-800',
      readonly: 'bg-gray-100 text-gray-800'
    }
    return colors[role]
  }

  return (
    <div className="p-6 space-y-6">
      <DebugInfo />
      
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Administração</h1>
          <p className="text-muted-foreground">Gerenciamento de usuários e permissões</p>
        </div>
        
        <div className="flex gap-2">
          <Button 
            variant="outline"
            onClick={resetElvioAdmin}
            className="mr-2"
          >
            <Shield size={16} className="mr-2" />
            Reset Elvio Admin
          </Button>
          
          <Button 
            variant="outline"
            onClick={fixAdminPermissions}
            className="mr-2"
          >
            <Wrench size={16} className="mr-2" />
            Corrigir Permissões
          </Button>
          
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button onClick={() => { setEditingUser(null); setFormData({ username: '', name: '', email: '', role: 'recepcao' }); }}>
                <Plus size={16} className="mr-2" />
                Novo Usuário
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>{editingUser ? 'Editar Usuário' : 'Criar Novo Usuário'}</DialogTitle>
              <DialogDescription>
                {editingUser ? 'Edite as informações do usuário' : 'Adicione um novo usuário ao sistema'}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nome Completo *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Nome completo"
                />
              </div>

              {!editingUser && (
                <div className="space-y-2">
                  <Label htmlFor="username">Nome de Usuário *</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                    placeholder="nome.usuario"
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="usuario@4mcontabilidade.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Função *</Label>
                <Select 
                  value={formData.role} 
                  onValueChange={(value: UserRole) => setFormData(prev => ({ ...prev, role: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="recepcao">Recepção</SelectItem>
                    <SelectItem value="fiscal">Fiscal</SelectItem>
                    <SelectItem value="financeiro">Financeiro</SelectItem>
                    <SelectItem value="contabil">Contábil</SelectItem>
                    <SelectItem value="rh">Recursos Humanos</SelectItem>
                    <SelectItem value="gerencial">Gerencial</SelectItem>
                    <SelectItem value="readonly">Somente Leitura</SelectItem>
                    {currentUser?.role === 'admin' && (
                      <SelectItem value="admin">Administrador</SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>

              {!editingUser && (
                <div className="bg-muted p-3 rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    <strong>Senha padrão:</strong> {formData.username}123
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    O usuário deve alterar a senha no primeiro acesso
                  </p>
                </div>
              )}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancelar
              </Button>
              <Button onClick={editingUser ? handleUpdateUser : handleCreateUser}>
                {editingUser ? 'Salvar' : 'Criar'}
              </Button>
            </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Users Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Users className="text-primary" size={20} />
              <div>
                <p className="text-2xl font-bold">{(users || []).length}</p>
                <p className="text-xs text-muted-foreground">Total de Usuários</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <UserCheck className="text-green-600" size={20} />
              <div>
                <p className="text-2xl font-bold">{(users || []).filter(u => u.isActive).length}</p>
                <p className="text-xs text-muted-foreground">Usuários Ativos</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Shield className="text-blue-600" size={20} />
              <div>
                <p className="text-2xl font-bold">{(users || []).filter(u => u.role === 'admin').length}</p>
                <p className="text-xs text-muted-foreground">Administradores</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Clock className="text-orange-600" size={20} />
              <div>
                <p className="text-2xl font-bold">{(users || []).filter(u => u.lastLogin).length}</p>
                <p className="text-xs text-muted-foreground">Já Logaram</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Usuários do Sistema</CardTitle>
          <CardDescription>Gerencie todos os usuários e suas permissões</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Usuário</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Função</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Último Acesso</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(users || []).map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{user.name}</p>
                      <p className="text-sm text-muted-foreground">@{user.username}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Envelope size={14} className="text-muted-foreground" />
                      <span className="text-sm">{user.email}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getRoleColor(user.role)}>
                      {getRoleLabel(user.role)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={user.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {user.isActive ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {user.lastLogin ? (
                      new Date(user.lastLogin).toLocaleDateString('pt-BR')
                    ) : (
                      <span className="text-muted-foreground">Nunca</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditUser(user)}
                      >
                        <Pencil size={16} />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleUserStatus(user)}
                        disabled={user.id === currentUser?.id}
                      >
                        {user.isActive ? <UserCheck size={16} /> : <Key size={16} />}
                      </Button>
                      {user.id !== currentUser?.id && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteUser(user)}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash size={16} />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
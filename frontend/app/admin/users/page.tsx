"use client";
import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Users, UserX, Shield, User } from "lucide-react";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";

interface UserRecord {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    try {
      const res = await apiClient.get("/admin/users?limit=100");
      setUsers(res.data.items);
      setTotal(res.data.total);
    } catch { /* ignore */ }
  };

  const updateRole = async (userId: string, role: string) => {
    try {
      await apiClient.patch(`/admin/users/${userId}`, { role });
      toast.success("Role updated");
      setUsers((prev) => prev.map((u) => u.id === userId ? { ...u, role } : u));
    } catch { toast.error("Failed to update role"); }
  };

  const toggleActive = async (userId: string, currentActive: boolean) => {
    try {
      await apiClient.patch(`/admin/users/${userId}`, { is_active: !currentActive });
      toast.success(currentActive ? "User deactivated" : "User activated");
      setUsers((prev) => prev.map((u) => u.id === userId ? { ...u, is_active: !currentActive } : u));
    } catch { toast.error("Failed to update status"); }
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text">Users</h1>
        <p className="text-muted-foreground mt-1">{total} total users</p>
      </div>

      <Card className="glass border-border/50">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Joined</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium text-sm">{user.email}</TableCell>
                  <TableCell>
                    <Select value={user.role} onValueChange={(val: string | null) => val && updateRole(user.id, val)}>
                      <SelectTrigger className="h-7 w-24 text-xs bg-secondary/30 border-border/50">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="user"><span className="flex items-center gap-1"><User className="w-3 h-3" />user</span></SelectItem>
                        <SelectItem value="admin"><span className="flex items-center gap-1"><Shield className="w-3 h-3" />admin</span></SelectItem>
                      </SelectContent>
                    </Select>
                  </TableCell>
                  <TableCell>
                    <Badge variant={user.is_active ? "default" : "secondary"} className="text-xs">
                      {user.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(user.created_at), { addSuffix: true })}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" className="h-7 text-xs"
                      onClick={() => toggleActive(user.id, user.is_active)}>
                      <UserX className="w-3.5 h-3.5 mr-1" />
                      {user.is_active ? "Deactivate" : "Activate"}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

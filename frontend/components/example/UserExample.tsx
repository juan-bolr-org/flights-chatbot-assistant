// Example component showing how to use the new authentication system

import { useUser, useToken } from '@/context/UserContext';

export function UserExample() {
  const { user, loading, refreshUser } = useUser();
  const token = useToken();

  if (loading) {
    return <div>Loading user...</div>;
  }

  if (!user) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <h2>Current User</h2>
      <p>Name: {user.name}</p>
      <p>Email: {user.email}</p>
      <p>ID: {user.id}</p>
      {token && <p>Token exists: ✓</p>}
      
      <button onClick={refreshUser}>
        Refresh User Data
      </button>
    </div>
  );
}

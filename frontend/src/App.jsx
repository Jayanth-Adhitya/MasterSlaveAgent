import { useState, useEffect, useCallback, useRef } from 'react';
import { Login } from './components/Login';
import { Chat } from './components/Chat';
import { Notifications } from './components/Notifications';
import { useWebSocket } from './hooks/useWebSocket';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [userInfo, setUserInfo] = useState(null);
  const [sessionId, setSessionId] = useState(
    localStorage.getItem('sessionId') || generateSessionId()
  );
  const addMessageRef = useRef(null);

  // Parse JWT to get user info
  useEffect(() => {
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUserInfo({
          userId: payload.user_id,
          tenantId: payload.tenant_id,
          email: payload.email,
          name: payload.name,
          role: payload.role,
          tenantName: payload.tenant_name,
          tenantType: payload.tenant_type,
        });
      } catch (error) {
        console.error('Failed to parse token:', error);
        handleLogout();
      }
    }
  }, [token]);

  // Save session ID
  useEffect(() => {
    localStorage.setItem('sessionId', sessionId);
  }, [sessionId]);

  const handleWebSocketMessage = useCallback((data) => {
    console.log('WebSocket message:', data);
    if (data.type === 'message' && addMessageRef.current) {
      addMessageRef.current(data.content);
    } else if (data.type === 'error' && addMessageRef.current) {
      addMessageRef.current(data.content);
    }
  }, []);

  const { connected } = useWebSocket(token, handleWebSocketMessage);

  const handleLogin = (accessToken) => {
    localStorage.setItem('token', accessToken);
    setToken(accessToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUserInfo(null);
  };

  const handleNewSession = () => {
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
  };

  const setAddMessage = useCallback((fn) => {
    addMessageRef.current = fn;
  }, []);

  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="container">
      <div className="header">
        <div className="user-info">
          <div>
            <strong>{userInfo?.tenantName}</strong> ({userInfo?.tenantType})
          </div>
          <div>
            {userInfo?.name} - {userInfo?.role}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div
            className={`connection-status ${connected ? 'connected' : 'disconnected'}`}
          >
            {connected ? '● Connected' : '○ Disconnected'}
          </div>
          <Notifications token={token} />
          <button onClick={handleNewSession} className="btn btn-secondary">
            New Chat
          </button>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>

      <Chat token={token} sessionId={sessionId} onNewMessage={setAddMessage} />
    </div>
  );
}

function generateSessionId() {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export default App;

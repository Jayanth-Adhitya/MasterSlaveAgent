import { useState } from 'react';
import { login } from '../services/api';

export function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await login(email, password);
      onLogin(data.access_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Agent Prototype</h2>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            required
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
        {error && <div className="error">{error}</div>}
        <div style={{ marginTop: '20px', padding: '15px', background: '#f5f5f5', borderRadius: '8px', fontSize: '14px', color: '#333' }}>
          <strong style={{ fontSize: '15px', color: '#000' }}>Demo Restaurant Accounts</strong>
          <div style={{ marginTop: '10px', lineHeight: '1.8' }}>
            <div><strong>Mario</strong> (Manager): <code>mario@pizza.com</code></div>
            <div><strong>Luigi</strong> (Employee): <code>luigi@pizza.com</code></div>
            <div><strong>Peach</strong> (Employee): <code>peach@pizza.com</code></div>
            <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #ddd' }}>
              <strong>Password:</strong> <code>password123</code>
            </div>
            <div style={{ marginTop: '10px', fontSize: '13px', color: '#666', fontStyle: 'italic' }}>
              💡 Tip: Login as Mario to send messages. The AI can notify Luigi or Peach based on the restaurant schedule and roster.
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}

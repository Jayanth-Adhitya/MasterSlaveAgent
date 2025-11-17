import { useState, useEffect } from 'react';
import {
  getNotifications,
  getUnreadCount,
  markNotificationRead,
} from '../services/api';

export function Notifications({ token }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showPanel, setShowPanel] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUnreadCount();
    const interval = setInterval(loadUnreadCount, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, [token]);

  const loadUnreadCount = async () => {
    try {
      const data = await getUnreadCount(token);
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error('Failed to load unread count:', error);
    }
  };

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const data = await getNotifications(token);
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePanel = () => {
    if (!showPanel) {
      loadNotifications();
    }
    setShowPanel(!showPanel);
  };

  const handleMarkRead = async (notificationId) => {
    try {
      await markNotificationRead(token, notificationId);
      setNotifications((prev) =>
        prev.map((n) => (n.id === notificationId ? { ...n, read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div>
      <div className="notifications-badge" onClick={handleTogglePanel}>
        <button className="btn btn-secondary">
          🔔 Notifications
          {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
        </button>
      </div>

      {showPanel && (
        <div className="notifications-panel">
          <div style={{ padding: '15px', borderBottom: '1px solid #ddd' }}>
            <strong>Notifications</strong>
            <button
              onClick={() => setShowPanel(false)}
              style={{ float: 'right', border: 'none', background: 'none', cursor: 'pointer' }}
            >
              ✕
            </button>
          </div>
          {loading ? (
            <div className="loading">Loading...</div>
          ) : notifications.length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
              No notifications
            </div>
          ) : (
            notifications.map((notification) => (
              <div
                key={notification.id}
                className={`notification-item ${!notification.read ? 'unread' : ''}`}
                onClick={() => !notification.read && handleMarkRead(notification.id)}
              >
                <div className="notification-from">
                  From: {notification.from_user_name}
                </div>
                <div className="notification-message">{notification.message}</div>
                <div className="notification-time">
                  {formatTime(notification.created_at)}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

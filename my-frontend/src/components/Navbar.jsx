// src/components/Navbar.jsx (یا کامپوننت زنگوله شما)
import React, { useState, useEffect, useRef } from 'react';
import { Bell } from 'lucide-react';

export default function Navbar() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    // 🌟 اتصال به وب‌سوکت نوتیفیکیشن بک‌آند
    const token =
      localStorage.getItem('token') || localStorage.getItem('access_token');
    const wsProtocol =
      window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${wsProtocol}localhost:8000/ws/notifications/?token=${token || ''}`;

    socketRef.current = new WebSocket(wsUrl);

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // اضافه کردن نوتیفیکیشن جدید به ابتدای لیست
      setNotifications((prev) => [data, ...prev]);
      setUnreadCount((prev) => prev + 1);
    };

    return () => {
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  const handleOpenDropdown = () => {
    setIsOpen(!isOpen);
    setUnreadCount(0); // صفر کردن شمارنده بعد از باز کردن منو
  };

  return (
    <div className="relative" dir="rtl">
      {/* دکمه زنگوله */}
      <button
        onClick={handleOpenDropdown}
        className="relative p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-all"
      >
        <Bell size={22} className={unreadCount > 0 ? 'animate-bounce' : ''} />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 bg-red-500 text-white text-xs w-4 h-4 flex items-center justify-center rounded-full font-bold">
            {unreadCount}
          </span>
        )}
      </button>

      {/* منوی بازشوی نوتیفیکیشن‌ها */}
      {isOpen && (
        <div className="absolute left-0 mt-2 w-72 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-lg py-2 z-50">
          <div className="px-4 py-2 font-bold text-xs text-gray-400 border-b border-gray-100 dark:border-gray-800">
            اعلان‌های اخیر
          </div>
          <div className="max-h-60 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="px-4 py-6 text-sm text-center text-gray-400">
                هیچ اعلانی وجود ندارد
              </div>
            ) : (
              notifications.map((notif, index) => (
                <div
                  key={index}
                  className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 text-sm text-gray-700 dark:text-gray-200 border-b border-gray-50 dark:border-gray-800/30 transition-all"
                >
                  {notif.message}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

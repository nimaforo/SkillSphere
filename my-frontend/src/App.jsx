// src/App.jsx
import React, { useState, useEffect } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import Sidebar from './components/Sidebar';
import ThemeToggle from './components/ThemeToggle';
import Dashboard from './pages/Dashboard';
import ProjectManagement from './pages/ProjectManagement';
import Profile from './pages/Profile';
import Chat from './pages/Chat';
import Auth from './pages/Auth';
import { Bell, MessageSquare, Heart, Info, LogOut, Trash2 } from 'lucide-react';
import ProjectFeed from './pages/ProjectFeed';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [userName, setUserName] = useState('کاربر');  // Add user name state
  const [userEmail, setUserEmail] = useState('');  // Add user email state

  // بررسی وضعیت لاگین در اولین رندر
  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('🔍 App loading - checking for stored token:', token ? '✅ Found' : '❌ Not found');
    
    if (token) {
      // Verify token is still valid by making a test request
      verifyToken(token);
    }
  }, []);

  // Verify if stored token is still valid
  const verifyToken = async (token) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/projects/analytics/', {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        console.log('✅ Token is valid');
        setIsAuthenticated(true);
        
        // Get user data from analytics endpoint
        const data = response.json();
        data.then(result => {
          if (result.user) {
            setUserName(result.user.name || result.user.email.split('@')[0]);
            setUserEmail(result.user.email);
          }
        });
        
        fetchSavedNotifications(token);
      } else if (response.status === 401) {
        console.log('⚠️ Token expired or invalid - clearing');
        localStorage.removeItem('token');
        setIsAuthenticated(false);
      }
    } catch (err) {
      console.error('Error verifying token:', err);
    }
  };

  // دریافت اعلان‌های قدیمی و واقعی از دیتابیس جنگو
  const fetchSavedNotifications = async (token) => {
    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/projects/notifications/',
        {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        console.log('✅ اعلان‌ها دریافت شدند:', data);

        // مپ کردن داده‌های دریافتی دیتابیس با ساختار استیت فرانت‌آند
        // data.results است (array) یا فقط array
        const notificationsList = data.results || data || [];
        const formattedNotifications = notificationsList.map((n) => ({
          id: n.id,
          text: n.message,
          type: n.notification_type, // 'LIKE' یا 'COMMENT'
          time: new Date(n.created_at).toLocaleTimeString('fa-IR', {
            hour: '2-digit',
            minute: '2-digit',
          }),
        }));
        setNotifications(formattedNotifications);
      } else if (response.status === 401) {
        handleLogout(); // اگر توکن منقضی شده بود، کاربر هدایت شود به صفحه لاگین
      } else {
        console.warn('⚠️ Response status:', response.status);
      }
    } catch (err) {
      console.error('خطا در بارگذاری اعلان‌های دیتابیس:', err);
    }
  };

  // 📡 اتصال به وب‌سوکت اختصاصی (دارای لایه احراز هویت JWT)
  useEffect(() => {
    if (!isAuthenticated) return;

    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('⚠️ توکن یافت نشد');
      return;
    }

    // اتصال به WebSocket برای اعلان‌های real-time
    // توکن JWT در query string ارسال می‌شود
    const socketUrl = `ws://127.0.0.1:8000/ws/notifications/?token=${token}`;
    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;

    const connectWebSocket = () => {
      try {
        socket = new WebSocket(socketUrl);

        socket.onopen = () => {
          console.log('✅ اتصال WebSocket اعلان‌ها برقرار شد');
          reconnectAttempts = 0; // Reset on successful connection
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('🔔 اعلان دریافت شد:', data);

            // نوتیفیکیشن را به state اضافه کن
            const newNotification = {
              id: data.id || Date.now(),
              text: data.message,
              type: data.type || data.notification_type,
              time: 'هم‌اکنون',
            };

            setNotifications((prev) => [newNotification, ...prev]);
          } catch (error) {
            console.error('❌ خطا در پارس اعلان:', error);
          }
        };

        socket.onclose = (e) => {
          console.log('🔌 اتصال WebSocket قطع شد. کد:', e.code);

          // تلاش برای اتصال دوباره
          if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            console.log(
              `🔄 تلاش مجدد برای اتصال... (تلاش ${reconnectAttempts}/${maxReconnectAttempts})`
            );
            setTimeout(() => {
              connectWebSocket();
            }, 3000 * reconnectAttempts); // Exponential backoff
          } else {
            console.error('❌ نتوانست به WebSocket متصل شود');
          }
        };

        socket.onerror = (err) => {
          console.error('❌ خطای WebSocket:', err);
        };
      } catch (error) {
        console.error('❌ خطا در ساختن WebSocket:', error);
      }
    };

    connectWebSocket();

    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [isAuthenticated]);

  const handleClearAllNotifications = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        'http://127.0.0.1:8000/api/projects/notifications/clear-all/',
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: 'application/json',
          },
        }
      );
      if (response.ok) {
        setNotifications([]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setNotifications([]);
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'LIKE':
        return <Heart size={16} className="text-red-500" />;
      case 'COMMENT':
        return <MessageSquare size={16} className="text-blue-500" />;
      default:
        return <Info size={16} className="text-gray-500" />;
    }
  };

  // اگر احراز هویت انجام نشده، فرم لاگین/ثبت‌نام بیاید
  if (!isAuthenticated) {
    return <Auth onAuthSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <ThemeProvider>
      <div
        className="min-h-screen bg-gray-50 dark:bg-black font-sans transition-colors"
        dir="rtl"
      >
        <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

        <div className="pr-64">
          <header className="h-16 border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-50">
            <div className="text-gray-400 text-sm">خوش آمدید، {userName} 👋</div>
            <div className="flex items-center gap-4 relative">
              {/* دکمه اعلان‌ها */}
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg relative cursor-pointer"
              >
                <Bell size={20} />
                {notifications.length > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                )}
              </button>

              {/* باکس کشویی اعلان‌ها */}
              {showNotifications && (
                <div className="absolute left-0 top-12 w-80 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl shadow-xl p-4 z-50 space-y-3">
                  <div className="flex justify-between items-center border-b border-gray-100 dark:border-gray-800 pb-2">
                    <h3 className="font-bold text-gray-800 dark:text-white text-sm">
                      اعلان‌های سیستم
                    </h3>
                    {notifications.length > 0 && (
                      <button
                        onClick={handleClearAllNotifications}
                        className="text-[10px] text-red-500 hover:underline flex items-center gap-1 cursor-pointer"
                      >
                        <Trash2 size={10} /> پاک کردن همه
                      </button>
                    )}
                  </div>

                  {notifications.length === 0 ? (
                    <p className="text-xs text-gray-400 text-center py-4">
                      اعلان جدیدی وجود ندارد.
                    </p>
                  ) : (
                    <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
                      {notifications.map((n) => (
                        <div
                          key={n.id}
                          className="flex gap-3 items-start p-2 hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded-xl transition-all cursor-pointer"
                        >
                          <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded-lg shrink-0">
                            {getNotificationIcon(n.type)}
                          </div>
                          <div className="flex-1">
                            <p className="text-xs font-medium text-gray-700 dark:text-gray-300 leading-snug">
                              {n.text}
                            </p>
                            <span className="text-[10px] text-gray-400 mt-1 block">
                              {n.time}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <ThemeToggle />

              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-red-500 rounded-lg cursor-pointer transition-colors"
                title="خروج از حساب"
              >
                <LogOut size={20} />
              </button>
            </div>
          </header>

          <main className="p-8">
            {/* 🌟 فرستادن کلید یا توکن به کامپوننت‌ها برای اطمینان از دسترسی به هدر درست */}
            {currentTab === 'dashboard' && <Dashboard />}
            {currentTab === 'projects' && <ProjectManagement />}
            {currentTab === 'profile' && <Profile />}
            {currentTab === 'chat' && <Chat />}
            {currentTab === 'project_feed' && <ProjectFeed />}
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
}

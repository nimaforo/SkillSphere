// src/pages/Chat.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    // Get token from localStorage
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('❌ No token found - cannot connect to chat');
      return;
    }

    // Connect to WebSocket with token
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${wsProtocol}localhost:8000/ws/chat/1/?token=${token}`;
    
    console.log('📡 Connecting to chat WebSocket...');
    socketRef.current = new WebSocket(wsUrl);

    socketRef.current.onopen = () => {
      console.log('✅ Chat WebSocket connected');
      setIsConnected(true);
    };

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 Message received:', data);
      if (data.message) {
        setMessages((prev) => [...prev, {
          message: data.message,
          username: data.username,
          timestamp: new Date().toLocaleTimeString('fa-IR')
        }]);
      }
    };

    socketRef.current.onclose = (e) => {
      console.log(`❌ Chat WebSocket closed. Code: ${e.code}`);
      setIsConnected(false);
    };

    socketRef.current.onerror = (err) => {
      console.error('❌ Chat WebSocket error:', err);
      setIsConnected(false);
    };

    return () => {
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // ارسال پیام به جنگو چنلز
    socketRef.current.send(
      JSON.stringify({
        message: inputMessage,
      })
    );

    setInputMessage('');
  };

  return (
    <div className="max-w-xl bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm flex flex-col h-[500px]">
      <div className="p-4 border-b border-gray-100 dark:border-gray-800 font-bold text-gray-800 dark:text-white">
        اتاق چت آنلاین
      </div>

      {/* لیست پیام‌ها */}
      <div
        className="flex-1 p-4 overflow-y-auto space-y-2 flex flex-col"
        dir="rtl"
      >
        {!isConnected && (
          <div className="text-yellow-600 dark:text-yellow-400 text-center text-sm p-2 bg-yellow-50 dark:bg-yellow-950/30 rounded-lg">
            ⚠️ در حال اتصال...
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={index} className="space-y-1">
            <div className="text-xs text-gray-500 dark:text-gray-400 px-3">
              {msg.username} • {msg.timestamp}
            </div>
            <div
              className="bg-blue-600 text-white p-3 rounded-2xl rounded-br-none max-w-[80%] w-fit self-start"
            >
              {msg.message}
            </div>
          </div>
        ))}
        {messages.length === 0 && (
          <div className="text-gray-400 text-center text-sm mt-20">
            {isConnected ? 'هیچ پیامی هنوز ارسال نشده است' : 'درحال اتصال به سرور...'}
          </div>
        )}
      </div>

      {/* فرم ارسال */}
      <form
        onSubmit={handleSendMessage}
        className="p-4 border-t border-gray-100 dark:border-gray-800 flex gap-2"
      >
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="پیام خود را بنویسید..."
          className="flex-1 bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-white px-4 py-2 rounded-xl focus:outline-none focus:border-blue-500 border border-transparent dark:border-gray-700"
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-xl cursor-pointer transition-all"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
}

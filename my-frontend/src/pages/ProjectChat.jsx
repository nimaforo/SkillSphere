// src/pages/ProjectChat.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Send, MessageSquare } from 'lucide-react';

export default function ProjectChat({ projectId }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false); // 🌟 وضعیت اتصال وب‌سوکت
  const socketRef = useRef(null);

  useEffect(() => {
    if (!projectId) return;

    // ۱. استخراج توکن احراز هویت از لایه ذخیره‌سازی مرورگر
    const token =
      localStorage.getItem('token') || localStorage.getItem('access_token');

    // ۲. بررسی خودکار پروتکل امن یا عادی (ws vs wss)
    const wsProtocol =
      window.location.protocol === 'https:' ? 'wss://' : 'ws://';

    // ۳. تزریق توکن به عنوان پارامتر کوئری برای هندل چنلز بک‌آند
    const wsUrl = `${wsProtocol}localhost:8000/ws/chat/${projectId}/?token=${token || ''}`;

    console.log('در حال تلاش برای برقراری اتصال چت زنده:', wsUrl);
    socketRef.current = new WebSocket(wsUrl);

    socketRef.current.onopen = () => {
      console.log(
        `اتصال وب‌سوکت چت برای پروژه ${projectId} با موفقیت تایید شد.`
      );
      setIsConnected(true);
    };

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    socketRef.current.onclose = (e) => {
      console.log(
        `اتصال وب‌سوکت چت پروژه ${projectId} بسته شد. کد وضعیت: ${e.code}`
      );
      setIsConnected(false);
    };

    socketRef.current.onerror = (err) => {
      console.error('خطای سیستمی وب‌سوکت چت:', err);
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [projectId]);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    if (socketRef.current && isConnected) {
      socketRef.current.send(
        JSON.stringify({
          message: inputMessage,
          sender: 'نیما فکری',
        })
      );
      setInputMessage('');
    } else {
      alert(
        'ارسال پیام امکان‌پذیر نیست. لطفاً از اتصال سرور و ورود به اکانت خود مطمئن شوید.'
      );
    }
  };

  return (
    <div
      className="flex flex-col h-[500px] bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden"
      dir="rtl"
    >
      {/* Header */}
      <div className="bg-gray-50 dark:bg-gray-800/50 p-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare className="text-blue-500" size={20} />
          <h3 className="font-bold text-gray-800 dark:text-white text-sm">
            اتاق گفتگو
          </h3>
        </div>
        {/* نشانگر زنده وضعیت اتصال */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">
            {isConnected ? 'متصل' : 'قطع اتصال'}
          </span>
          <span
            className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}
          ></span>
        </div>
      </div>

      {/* Messages List */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex flex-col ${msg.sender === 'نیما فکری' ? 'items-start' : 'items-end'}`}
          >
            <span className="text-xs text-gray-400 mb-1">{msg.sender}</span>
            <div
              className={`p-3 rounded-2xl text-sm max-w-xs ${
                msg.sender === 'نیما فکری'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none'
              }`}
            >
              {msg.message}
            </div>
          </div>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={sendMessage}
        className="p-4 border-t border-gray-100 dark:border-gray-800 flex gap-2"
      >
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={
            isConnected
              ? 'پیام خود را بنویسید...'
              : 'در حال تایید هویت و اتصال...'
          }
          disabled={!isConnected}
          className="flex-1 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-white px-4 py-2 rounded-xl focus:outline-none focus:border-blue-500 text-sm disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!isConnected}
          className="bg-blue-600 hover:bg-blue-700 text-white p-2.5 rounded-xl transition-all disabled:opacity-50"
        >
          <Send size={18} className="transform rotate-180" />
        </button>
      </form>
    </div>
  );
}

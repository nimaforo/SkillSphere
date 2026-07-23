// src/pages/Auth.jsx
import React, { useState } from 'react';
import { Lock, Mail, Eye, EyeOff, LogIn, UserPlus, User } from 'lucide-react';

export default function Auth({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (isLogin) {
      // --- ۱. درخواست واقعی ورود به جنگو ---
      try {
        const response = await fetch('http://localhost:8000/api/login/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: email, password: password }),
        });

        const data = await response.json();

        if (response.ok) {
          const token = data.access || data.token;
          console.log('✅ Login successful, storing token:', token ? 'Token saved' : 'No token!');
          
          if (token) {
            localStorage.setItem('token', token);
            // Force a small delay to ensure token is stored
            setTimeout(() => {
              onAuthSuccess();
            }, 100);
          } else {
            setError('خطای سرور: توکن دریافت نشد');
          }
        } else {
          setError(data.detail || 'ایمیل یا رمز عبور اشتباه است!');
        }
      } catch (err) {
        setError('خطا در اتصال به سرور بک‌آند! مطمئن شوید داکر روشن است.');
      }
    } else {
      // --- ۲. درخواست واقعی ثبت‌نام در دیتابیس جنگو ---
      if (password !== confirmPassword) {
        setError('رمز عبور و تکرار آن با هم مطابقت ندارند!');
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/api/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: name,
            email: email,
            password: password,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          setSuccess(
            'ثبت‌نام با موفقیت انجام شد! در حال انتقال به صفحه ورود...'
          );
          console.log('✅ Registration successful');
          setTimeout(() => {
            setIsLogin(true);
            setName('');
            setEmail('');
            setPassword('');
            setConfirmPassword('');
          }, 2000);
        } else {
          setError(
            data.message || 'خطایی در ثبت‌نام رخ داد. اطلاعات را بررسی کنید.'
          );
        }
      } catch (err) {
        setError('خطا در اتصال به سرور! کانتینر جنگو را بررسی کنید.');
      }
    }
  };

  return (
    <div
      className="min-h-screen bg-gray-50 dark:bg-black flex items-center justify-center p-4 transition-colors"
      dir="rtl"
    >
      <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-8 shadow-xl space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
            {isLogin ? 'ورود به پنل مدیریت' : 'ایجاد حساب کاربری'}
          </h1>
          <p className="text-gray-400 text-sm">
            {isLogin
              ? 'خوش آمدید! لطفا اطلاعات خود را وارد کنید.'
              : 'برای عضویت، فرم زیر را تکمیل کنید.'}
          </p>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-950/30 text-red-500 text-xs p-3 rounded-xl font-medium">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 dark:bg-green-950/30 text-green-500 text-xs p-3 rounded-xl font-medium">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-2">
                نام و نام خانوادگی
              </label>
              <div className="relative">
                <User
                  className="absolute right-3 top-3 text-gray-400"
                  size={18}
                />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="نیما فکری"
                  className="w-full bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-white pr-10 pl-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500 text-sm"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-2">
              آدرس ایمیل
            </label>
            <div className="relative">
              <Mail
                className="absolute right-3 top-3 text-gray-400"
                size={18}
              />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-white pr-10 pl-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500 text-sm"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-2">
              رمز عبور
            </label>
            <div className="relative">
              <Lock
                className="absolute right-3 top-3 text-gray-400"
                size={18}
              />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-white pr-10 pl-12 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500 text-sm"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute left-3 top-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 cursor-pointer"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {!isLogin && (
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-2">
                تکرار رمز عبور
              </label>
              <div className="relative">
                <Lock
                  className="absolute right-3 top-3 text-gray-400"
                  size={18}
                />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-white pr-10 pl-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500 text-sm"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl font-medium transition-all cursor-pointer shadow-lg shadow-blue-500/20 text-sm"
          >
            {isLogin ? <LogIn size={18} /> : <UserPlus size={18} />}
            <span>{isLogin ? 'ورود به حساب' : 'ثبت نام و عضویت'}</span>
          </button>
        </form>

        <div className="text-center pt-2 border-t border-gray-100 dark:border-gray-800">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
              setSuccess('');
            }}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline cursor-pointer font-medium"
          >
            {isLogin
              ? 'هنوز حساب کاربری ندارید؟ ثبت‌نام کنید'
              : 'قبلاً ثبت‌نام کرده‌اید؟ وارد شوید'}
          </button>
        </div>
      </div>
    </div>
  );
}

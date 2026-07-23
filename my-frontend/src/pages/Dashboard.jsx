// src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  Users,
  Briefcase,
  MessageSquare,
  FolderHeart,
  BarChart3,
} from 'lucide-react';

const weeklyPlaceholderData = [
  { name: 'شنبه', pv: 2400 },
  { name: 'یکشنبه', pv: 1398 },
  { name: 'دوشنبه', pv: 9800 },
  { name: 'سه‌شنبه', pv: 3908 },
  { name: 'چهارشنبه', pv: 4800 },
  { name: 'پنجشنبه', pv: 3800 },
  { name: 'جمعه', pv: 4300 },
];

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // واکشی دیتای واقعی آنالیتیکس از بک‌آند جنگو
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(
          'http://127.0.0.1:8000/api/projects/analytics/',
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
          console.log('✅ Analytics fetched:', data);
          setStats(data);
        } else {
          console.warn('Analytics response status:', response.status);
          // Use placeholder data on error
          setStats({
            summary: { total_users: 0, total_projects: 0, total_comments: 0 },
            popular_project: null,
            top_uploaders: [],
          });
        }
      } catch (error) {
        console.error('خطا در دریافت آمار واقعی:', error);
        // Use placeholder data on error
        setStats({
          summary: { total_users: 0, total_projects: 0, total_comments: 0 },
          popular_project: null,
          top_uploaders: [],
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div
        className="text-center text-gray-500 text-sm py-12 animate-pulse"
        dir="rtl"
      >
        در حال تحلیل و بارگذاری آمارهای زنده سیستم...
      </div>
    );
  }

  return (
    <div className="space-y-6" dir="rtl">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
        خلاصه وضعیت سیستم
      </h1>

      {/* Cards - متصل به دیتای واقعی */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          {
            title: 'کاربران ثبت‌نام شده',
            value: stats?.summary?.total_users || 0,
            icon: Users,
            color: 'text-green-500',
          },
          {
            title: 'کل پروژه‌های ارسالی',
            value: stats?.summary?.total_projects || 0,
            icon: Briefcase,
            color: 'text-blue-500',
          },
          {
            title: 'کل تعاملات و نظرات',
            value: (stats?.summary?.total_comments || 0) + (stats?.summary?.total_notifications || 0),
            icon: MessageSquare,
            color: 'text-purple-500',
          },
        ].map((card, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm flex items-center justify-between"
          >
            <div>
              <span className="text-gray-400 text-sm font-medium">
                {card.title}
              </span>
              <h3 className="text-2xl font-bold text-gray-800 dark:text-white mt-1">
                {card.value}
              </h3>
            </div>
            <div
              className={`p-3 rounded-xl bg-gray-50 dark:bg-gray-800 ${card.color}`}
            >
              <card.icon size={24} />
            </div>
          </div>
        ))}
      </div>

      {/* بخش تحلیل خطی سیستم (محبوب‌ترین پروژه و فعال‌ترین کاربران) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* باکس پروژه برتر */}
        <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm">
          <h3 className="text-sm font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
            <FolderHeart size={18} className="text-red-500" /> محبوب‌ترین پروژه
            ویترین
          </h3>
          {stats?.popular_projects && stats.popular_projects.length > 0 ? (
            <div className="bg-gray-50 dark:bg-gray-800/40 p-4 rounded-xl">
              <h4 className="text-xs font-bold text-gray-800 dark:text-white">
                {stats.popular_projects[0].title}
              </h4>
              <p className="text-[11px] text-gray-400 mt-1">
                آپلودکننده: {stats.popular_projects[0].user}
              </p>
              <div className="mt-3 text-xs font-semibold text-red-500 flex items-center gap-1">
                ❤️ {stats.popular_projects[0].likes} لایک تعاملی دریافت شده
              </div>
            </div>
          ) : (
            <p className="text-xs text-gray-400 py-4 text-center">
              هنوز پروژه‌ای لایک نشده است.
            </p>
          )}
        </div>

        {/* باکس کاربران فعال */}
        <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm">
          <h3 className="text-sm font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
            <BarChart3 size={18} className="text-amber-500" /> فعال‌ترین
            توسعه‌دهندگان سیستم
          </h3>
          <div className="space-y-2">
            {stats?.active_users && stats.active_users.length > 0 ? (
              stats.active_users.map((user, index) => (
                <div
                  key={index}
                  className="flex justify-between items-center bg-gray-50 dark:bg-gray-800/30 p-2.5 rounded-xl text-xs"
                >
                  <span className="text-gray-600 dark:text-gray-300 font-medium">
                    {user.email}
                  </span>
                  <span className="bg-blue-100 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 px-2.5 py-1 rounded-lg font-bold">
                    {user.activities} فعالیت
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-gray-400 py-4 text-center">
                کاربری یافت نشد.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm">
        <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
          آمار بازدید و تراکنش‌ها (هفتگی)
        </h3>

        <div className="h-[260px] w-full min-w-0">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={weeklyPlaceholderData}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
              <XAxis
                dataKey="name"
                stroke="#888888"
                fontSize={12}
                tickLine={false}
              />
              <YAxis stroke="#888888" fontSize={12} tickLine={false} />
              <Tooltip
                contentStyle={{
                  textAlign: 'right',
                  backgroundColor: '#1f2937',
                  borderColor: '#374151',
                  borderRadius: '0.5rem',
                  color: '#fff',
                }}
              />
              <Area
                type="monotone"
                dataKey="pv"
                stroke="#3b82f6"
                fillOpacity={0.1}
                fill="#3b82f6"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

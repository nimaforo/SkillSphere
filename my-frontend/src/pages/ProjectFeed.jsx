// src/pages/ProjectFeed.jsx
import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, Heart } from 'lucide-react';

export default function ProjectFeed() {
  const [projects, setProjects] = useState([]);
  const [commentInputs, setCommentInputs] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleSecureDownload = async (projectId, projectTitle) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://127.0.0.1:8000/api/projects/feed/${projectId}/download/`,
        {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: 'application/json',
          },
        }
      );

      if (response.ok) {
        // تبدیل فرمت باینری به آبجکت لوکال مرورگر جهت دانلود خودکار
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        // نام‌گذاری فایل با عنوان پروژه
        a.download = `${projectTitle || 'project_file'}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        alert('خطا در دانلود! شما دسترسی لازم را ندارید یا فایل حذف شده است.');
      }
    } catch (error) {
      console.error('خطای شبکه در دانلود امن:', error);
    }
  };
  // ۱. دریافت لیست پروژه‌ها از فید
  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/projects/feed/', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Projects fetched:', data);

        // Handle both formats: data.results (paginated) or direct array
        const projectsList = data.results || data || [];
        setProjects(projectsList);
      } else {
        console.warn('Response status:', response.status);
        setError('خطا در دریافت اطلاعات از سرور');
      }
    } catch (err) {
      console.error('Network Error:', err);
      setError('ارتباط با سرور برقرار نشد.');
    } finally {
      setLoading(false);
    }
  };

  // ۲. مدیریت لایک پروژه (هماهنگ با روت داکر شما)
  const handleLike = async (projectId) => {
    try {
      const token = localStorage.getItem('token');
      // اصلاح پث لایک بر اساس لاگ داکر شما
      const response = await fetch(
        `http://127.0.0.1:8000/api/projects/feed/${projectId}/like/`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json(); // خروجی بک‌آند: {"liked": true, "likes_count": 5}

        // بروزرسانی استیت لایک در فرانت‌آند
        setProjects((prevProjects) =>
          prevProjects.map((p) => {
            if (p.id === projectId) {
              return {
                ...p,
                likes_count: data.total_likes,
                is_liked_by_user: data.liked,
              };
            }
            return p;
          })
        );
      }
    } catch (err) {
      console.error('خطا در ثبت لایک:', err);
    }
  };

  // ۳. مدیریت ارسال کامنت جدید (حل مشکل ارور 404)
  const handleAddComment = async (projectId) => {
    const text = commentInputs[projectId] || '';
    if (!text.trim()) return;

    try {
      const token = localStorage.getItem('token');
      // اصلاح پث کامنت برای حل ارور 404 (اضافه کردن کلمه feed بر اساس ساختار روتینگ شما)
      const response = await fetch(
        `http://127.0.0.1:8000/api/projects/feed/${projectId}/comment/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
            Accept: 'application/json',
          },
          body: JSON.stringify({ content: text.trim() }),
        }
      );

      if (response.ok) {
        const responseData = await response.json();
        const newComment = responseData.comment;

        setProjects((prevProjects) =>
          prevProjects.map((p) => {
            if (p.id === projectId) {
              return {
                ...p,
                comments: [...(p.comments || []), newComment],
              };
            }
            return p;
          })
        );

        setCommentInputs((prev) => ({ ...prev, [projectId]: '' }));
      } else {
        console.error('خطا در ارسال کامنت به سرور');
      }
    } catch (error) {
      console.error('خطا در شبکه کامنت:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64 text-gray-500 dark:text-gray-400">
        <span className="text-sm font-medium animate-pulse">
          در حال بارگذاری ویترین پروژه‌ها...
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 text-red-600 dark:text-red-400 p-4 rounded-xl text-center text-sm">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        ویترین پروژه‌ها
      </h1>

      {projects.length === 0 ? (
        <p className="text-center text-gray-400 py-12 text-sm">
          هنوز هیچ پروژه‌ای آپلود نشده است.
        </p>
      ) : (
        projects.map((project) => (
          <div
            key={project.id}
            className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm transition-all"
          >
            {/* هدر پروژه */}
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-lg font-bold text-gray-800 dark:text-white">
                  {project.title}
                </h2>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  توسط: {project.user?.name || project.user?.email || 'نامشخص'}
                </p>
              </div>

              {/* ❤️ دکمه لایک اصلاح شده */}
              <button
                onClick={() => handleLike(project.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold cursor-pointer transition-all ${
                  project.is_liked_by_user
                    ? 'bg-red-50 dark:bg-red-950/40 text-red-500 border border-red-200 dark:border-red-900/50'
                    : 'bg-gray-50 dark:bg-gray-800 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Heart
                  size={14}
                  className={project.is_liked_by_user ? 'fill-current' : ''}
                />
                <span>{project.likes_count} لایک</span>
              </button>
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400 mt-3 leading-relaxed">
              {project.description}
            </p>

            {project.file_url && (
              <div className="mt-4">
                <button
                  onClick={() =>
                    handleSecureDownload(project.id, project.title)
                  }
                  className="inline-block text-xs text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/30 px-3 py-2 rounded-xl font-medium hover:underline cursor-pointer transition-all"
                >
                  📁 دانلود امن فایل پروژه (از طریق جریان API اختصاصی)
                </button>
              </div>
            )}

            <hr className="my-4 border-gray-100 dark:border-gray-800" />

            {/* کامنت‌ها */}
            <div className="space-y-3 max-h-48 overflow-y-auto mb-4 pr-1">
              {project.comments &&
                project.comments.map((comment) => (
                  <div
                    key={comment.id}
                    className="bg-gray-50 dark:bg-gray-800/40 p-3 rounded-xl flex flex-col gap-1"
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
                        {typeof comment.user === 'string' ? comment.user : (comment.user?.name || comment.user?.email || 'نامشخص')}
                      </span>
                      <span className="text-[10px] text-gray-400">
                        {comment.created_at
                          ? new Date(comment.created_at).toLocaleTimeString(
                              'fa-IR',
                              { hour: '2-digit', minute: '2-digit' }
                            )
                          : ''}
                      </span>
                    </div>
                    <p className="text-xs text-gray-700 dark:text-gray-300 pr-1">
                      {comment.content}
                    </p>
                  </div>
                ))}
            </div>

            {/* باکس ارسال کامنت جدید */}
            <div className="flex gap-2 items-center mt-3">
              <div className="relative flex-1">
                <input
                  type="text"
                  placeholder="نظر خود را بنویسید..."
                  value={commentInputs[project.id] || ''}
                  onChange={(e) =>
                    setCommentInputs((prev) => ({
                      ...prev,
                      [project.id]: e.target.value,
                    }))
                  }
                  onKeyDown={(e) =>
                    e.key === 'Enter' && handleAddComment(project.id)
                  }
                  className="w-full bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-white pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500 text-xs transition-colors"
                />
                <MessageSquare
                  size={16}
                  className="absolute left-3 top-3.5 text-gray-400"
                />
              </div>

              <button
                onClick={() => handleAddComment(project.id)}
                className="p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all cursor-pointer flex items-center justify-center shadow-md shadow-blue-500/10"
              >
                <Send size={16} className="rotate-180" />
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

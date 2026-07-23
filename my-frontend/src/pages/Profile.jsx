import React, { useState, useEffect } from 'react';
import {
  User,
  Mail,
  Save,
  CheckCircle,
  Heart,
  MessageSquare,
  FileText,
  Calendar,
  Edit2,
  Flame,
  Trophy,
  Target,
  TrendingUp,
  Award,
  Shield,
  Clock,
  Share2,
} from 'lucide-react';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [bio, setBio] = useState('');
  const [location, setLocation] = useState('');
  const [website, setWebsite] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/users/profile/', {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('📊 Profile loaded:', data);
        setProfile(data);
        setName(data.user.name);
        setBio(data.user.bio || '');
        setLocation(data.user.location || '');
        setWebsite(data.user.website || '');
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/users/profile/', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: name,
          bio: bio,
          location: location,
          website: website,
        }),
      });

      if (response.ok) {
        setSaved(true);
        setEditing(false);
        setTimeout(() => setSaved(false), 3000);
        fetchProfile();
      }
    } catch (error) {
      console.error('Error saving profile:', error);
    }
  };

  if (loading) {
    return (
      <div className="text-center text-gray-500 text-sm py-12 animate-pulse">
        در حال بارگذاری اطلاعات پروفایل...
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center text-gray-500 text-sm py-12">
        خطا در بارگذاری پروفایل
      </div>
    );
  }

  const stats = profile.stats;
  const initials = profile.user.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase();

  // Calculate engagement percentage
  const totalInteractions = stats.total_likes_received + stats.total_comments_on_projects;
  const engagementScore = Math.min(100, Math.round((totalInteractions / stats.total_projects) * 20));

  return (
    <div className="space-y-6" dir="rtl">
      {/* Main Profile Card with Cover */}
      <div className="relative">
        {/* Cover Image */}
        <div className="h-32 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-t-3xl shadow-lg"></div>

        {/* Profile Info Card */}
        <div className="bg-white dark:bg-gray-900 rounded-b-3xl border-x border-b border-gray-100 dark:border-gray-800 shadow-lg px-8 pb-8">
          {/* Avatar and Name */}
          <div className="flex items-end gap-6 -mt-16 mb-6">
            <div className="w-32 h-32 bg-gradient-to-br from-blue-400 to-purple-600 rounded-2xl flex items-center justify-center text-white text-4xl font-bold border-4 border-white dark:border-gray-900 shadow-xl">
              {initials}
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
                {profile.user.name}
              </h1>
              <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                @{profile.user.username}
              </p>
              {bio && (
                <p className="text-gray-600 dark:text-gray-300 mt-2 max-w-2xl">
                  {bio}
                </p>
              )}
            </div>
            <button
              onClick={() => setEditing(!editing)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-white px-6 py-3 rounded-xl font-medium transition-all cursor-pointer whitespace-nowrap"
            >
              <Edit2 size={16} />
              <span>{editing ? 'لغو' : 'ویرایش پروفایل'}</span>
            </button>
          </div>

          {/* Location and Website */}
          {!editing && (location || website) && (
            <div className="flex gap-6 mt-4 text-sm text-gray-600 dark:text-gray-400">
              {location && (
                <div className="flex items-center gap-2">
                  <Target size={14} />
                  <span>{location}</span>
                </div>
              )}
              {website && (
                <div className="flex items-center gap-2">
                  <Share2 size={14} />
                  <a href={website} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                    {website}
                  </a>
                </div>
              )}
            </div>
          )}

          {/* Success Message */}
          {saved && (
            <div className="flex items-center gap-2 bg-green-50 dark:bg-green-950/30 text-green-600 dark:text-green-400 p-4 rounded-xl text-sm font-medium mt-4">
              <CheckCircle size={18} />
              <span>پروفایل با موفقیت به‌روز شد!</span>
            </div>
          )}

          {/* Edit Mode */}
          {editing && (
            <div className="mt-6 space-y-4 p-6 bg-gray-50 dark:bg-gray-800/50 rounded-2xl">
              <div>
                <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                  نام و نام خانوادگی
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-white dark:bg-gray-800 text-gray-800 dark:text-white px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                  بیوگرافی
                </label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="درباره خود بنویسید..."
                  maxLength={160}
                  rows={3}
                  className="w-full bg-white dark:bg-gray-800 text-gray-800 dark:text-white px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500 resize-none"
                />
                <p className="text-xs text-gray-400 mt-1">{bio.length}/160</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                    شهر
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="تهران، ایران"
                    className="w-full bg-white dark:bg-gray-800 text-gray-800 dark:text-white px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                    وبسایت
                  </label>
                  <input
                    type="url"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    placeholder="https://example.com"
                    className="w-full bg-white dark:bg-gray-800 text-gray-800 dark:text-white px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <button
                onClick={handleSave}
                className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-3 rounded-xl font-medium transition-all cursor-pointer"
              >
                <Save size={18} />
                <span>ذخیره تغییرات</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Stats Grid - Enhanced */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                پروژه‌ها
              </p>
              <h3 className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">
                {stats.total_projects}
              </h3>
              <p className="text-xs text-gray-400 mt-1">کل ارسالی</p>
            </div>
            <FileText className="text-blue-500 opacity-30" size={32} />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                لایک‌ها
              </p>
              <h3 className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
                {stats.total_likes_received}
              </h3>
              <p className="text-xs text-gray-400 mt-1">دریافتی</p>
            </div>
            <Heart className="text-red-500 opacity-30" size={32} />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                نظرات
              </p>
              <h3 className="text-3xl font-bold text-amber-600 dark:text-amber-400 mt-2">
                {stats.total_comments_on_projects}
              </h3>
              <p className="text-xs text-gray-400 mt-1">دریافتی</p>
            </div>
            <MessageSquare className="text-amber-500 opacity-30" size={32} />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                فعالیت
              </p>
              <h3 className="text-3xl font-bold text-orange-600 dark:text-orange-400 mt-2">
                {stats.recent_activity_7days}
              </h3>
              <p className="text-xs text-gray-400 mt-1">۷ روز اخیر</p>
            </div>
            <Flame className="text-orange-500 opacity-30" size={32} />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                رتبه
              </p>
              <h3 className="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-2">
                {engagementScore}%
              </h3>
              <p className="text-xs text-gray-400 mt-1">درگیری</p>
            </div>
            <TrendingUp className="text-purple-500 opacity-30" size={32} />
          </div>
        </div>
      </div>

      {/* Achievements & Badges */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
        <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
          <Trophy size={20} className="text-amber-500" />
          افتخارات و موفقیت‌ها
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Achievement Badges */}
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20 rounded-xl p-4 text-center border border-amber-200 dark:border-amber-900/30">
            <div className="text-2xl mb-2">🎯</div>
            <p className="text-xs font-medium text-gray-700 dark:text-gray-300">
              کاربر فعال
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {stats.recent_activity_7days}+ فعالیت
            </p>
          </div>

          {stats.total_projects >= 3 && (
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 rounded-xl p-4 text-center border border-blue-200 dark:border-blue-900/30">
              <div className="text-2xl mb-2">📤</div>
              <p className="text-xs font-medium text-gray-700 dark:text-gray-300">
                سازنده
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {stats.total_projects} پروژه
              </p>
            </div>
          )}

          {stats.total_likes_received >= 5 && (
            <div className="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-950/20 dark:to-pink-950/20 rounded-xl p-4 text-center border border-red-200 dark:border-red-900/30">
              <div className="text-2xl mb-2">❤️</div>
              <p className="text-xs font-medium text-gray-700 dark:text-gray-300">
                محبوب
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {stats.total_likes_received} لایک
              </p>
            </div>
          )}

          {stats.total_comments_on_projects >= 3 && (
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 rounded-xl p-4 text-center border border-green-200 dark:border-green-900/30">
              <div className="text-2xl mb-2">💬</div>
              <p className="text-xs font-medium text-gray-700 dark:text-gray-300">
                مشارک‌کننده
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {stats.total_comments_on_projects} نظر
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Account Info */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
        <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
          <Shield size={20} className="text-blue-500" />
          اطلاعات حساب
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">ایمیل</p>
              <p className="text-sm font-medium text-gray-800 dark:text-white mt-1">
                {profile.user.email}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">نام کاربری</p>
              <p className="text-sm font-medium text-gray-800 dark:text-white mt-1">
                {profile.user.username}
              </p>
            </div>
          </div>
          <div className="space-y-4">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">عضویت</p>
              <p className="text-sm font-medium text-gray-800 dark:text-white mt-1 flex items-center gap-2">
                <Calendar size={14} />
                {new Date(profile.user.date_joined).toLocaleDateString('fa-IR')}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">شناسه کاربری</p>
              <p className="text-sm font-medium text-gray-800 dark:text-white mt-1">#{profile.user.id}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Projects */}
      {profile.recent_projects.length > 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
          <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
            <FileText size={20} className="text-blue-500" />
            پروژه‌های اخیر
          </h2>
          <div className="space-y-3">
            {profile.recent_projects.map((project, idx) => (
              <div
                key={project.id}
                className="flex items-center justify-between bg-gray-50 dark:bg-gray-800/30 p-4 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-all group"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center text-blue-600 dark:text-blue-400 text-sm font-bold">
                      {idx + 1}
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-800 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                        {project.title}
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {new Date(project.created_at).toLocaleDateString('fa-IR')}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-6 text-sm">
                  <div className="text-center">
                    <p className="text-lg font-bold text-red-500">{project.likes}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">❤️</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-amber-500">{project.comments}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">💬</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer Actions */}
      <div className="flex gap-3 justify-center">
        {/* Removed Settings and Download buttons */}
      </div>
    </div>
  );
}

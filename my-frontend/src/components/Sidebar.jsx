// src/components/Sidebar.jsx
// 🌟 اضافه کردن Compass به ایمپورت‌های lucide-react
import {
  LayoutDashboard,
  User,
  FolderKanban,
  MessageSquare,
  Compass,
} from 'lucide-react';

export default function Sidebar({ currentTab, setCurrentTab }) {
  const menus = [
    { id: 'dashboard', name: 'داشبورد', icon: LayoutDashboard },
    { id: 'projects', name: 'مدیریت پروژه‌ها', icon: FolderKanban },

    { id: 'project_feed', name: 'ویترین پروژه‌ها', icon: Compass },

    { id: 'profile', name: 'پروفایل کاربر', icon: User },
    { id: 'chat', name: 'اتاق چت آنلاین', icon: MessageSquare },
  ];

  return (
    <aside className="w-64 bg-white dark:bg-gray-900 h-screen fixed right-0 top-0 border-l border-gray-200 dark:border-gray-800 flex flex-col p-4 transition-colors">
      <div className="text-xl font-bold text-blue-600 dark:text-blue-400 mb-8 text-center">
        UPDOWN WEB PROJECT
      </div>
      <nav className="space-y-2 flex-1">
        {menus.map((menu) => {
          const Icon = menu.icon;
          return (
            <button
              key={menu.id}
              onClick={() => setCurrentTab(menu.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all cursor-pointer ${
                currentTab === menu.id
                  ? 'bg-blue-50 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
              }`}
            >
              <Icon size={20} />
              <span>{menu.name}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}

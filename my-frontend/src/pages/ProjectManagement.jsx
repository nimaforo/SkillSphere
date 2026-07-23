// C:/Users/nimaf/web project/my-frontend/src/pages/ProjectManagement.jsx
import React, { useState } from 'react';
import { UploadCloud, FileText, Download, Trash2, Loader2 } from 'lucide-react';

export default function ProjectManagement() {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false); // لودینگ برای زمان آپلود

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFilesToServer(e.dataTransfer.files);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      uploadFilesToServer(e.target.files);
    }
  };

  // 🌟 تابع اصلی ارسال فایل به بک‌آند جنگو با توکن JWT 🌟
  const uploadFilesToServer = async (selectedFiles) => {
    const token = localStorage.getItem('token'); // خواندن توکن از مرورگر
    if (!token) {
      alert('لطفاً ابتدا وارد حساب کاربری خود شوید.');
      return;
    }

    setLoading(true);

    // برای سادگی، فایل‌ها را یکی یکی آپلود می‌کنیم تا جنگو ولیدیت کند
    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      const formData = new FormData();

      // فیلدهای مورد نیاز دیتابیس جنگو
      formData.append('title', file.name);
      formData.append('description', 'آپلود شده از طریق فرانت‌اَند');
      formData.append('file', file);

      try {
        const response = await fetch(
          'http://localhost:8000/api/projects/upload/',
          {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token}`, // احراز هویت با JWT
            },
            body: formData,
          }
        );

        const data = await response.json();

        if (response.ok) {
          // ذخیره کردن اطلاعات واقعی بازگشتی از سرور
          const newUploadedFile = {
            id: data.project_id,
            name: file.name,
            size: (file.size / (1024 * 1024)).toFixed(2) + ' MB',
            url: `http://localhost:8000${data.file_url}`, // آدرس دانلود دایمی از داکر جنگو
          };
          setFiles((prevFiles) => [...prevFiles, newUploadedFile]);
        } else {
          // نمایش خطاهای فرمت و حجم که در مدل جنگو نوشتیم
          alert(
            `خطای سرور برای فایل ${file.name}: \n ${data.message || 'فرمت یا حجم غیرمجاز است!'}`
          );
        }
      } catch (err) {
        alert('خطا در اتصال به سرور بک‌آند! مطمئن شوید داکر روشن است.');
        console.error(err);
      }
    }
    setLoading(false);
  };

  const deleteFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
    // نکته: برای دلیت کردن از دیتابیس هم می‌توان بعداً API نوشت، فعلاً از لیست فرانت حذف می‌شود
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
        مدیریت پروژه‌ها و مستندات
      </h1>

      {/* Drag & Drop Zone */}
      <label
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all block cursor-pointer relative ${
          dragActive
            ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-950/20'
            : 'border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900'
        } ${loading ? 'opacity-50 pointer-events-none' : ''}`}
      >
        <input
          type="file"
          multiple
          className="hidden"
          onChange={handleFileChange}
          disabled={loading}
        />

        {loading ? (
          <div className="flex flex-col items-center justify-center">
            <Loader2 size={48} className="text-blue-500 animate-spin mb-4" />
            <p className="text-gray-700 dark:text-gray-300 font-medium">
              در حال آپلود و اعتبارسنجی امنیتی در سرور داکر...
            </p>
          </div>
        ) : (
          <>
            <UploadCloud
              size={48}
              className="mx-auto text-gray-400 dark:text-gray-600 mb-4"
            />
            <p className="text-gray-700 dark:text-gray-300 font-medium">
              فایل‌ها را اینجا رها کنید یا کلیک کنید
            </p>
            <span className="text-gray-400 text-xs mt-1 block">
              فرمت‌های مجاز: PDF, ZIP, تصاویر (حداکثر ۱۰ مگابایت)
            </span>
          </>
        )}
      </label>

      {/* File List */}
      {files.length > 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-2xl p-4 border border-gray-100 dark:border-gray-700 space-y-2">
          <h4 className="text-sm font-bold text-gray-500 mb-2">
            لیست فایل‌های پروژه (ذخیره شده در سرور):
          </h4>
          {files.map((file, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl"
            >
              <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                <FileText size={18} className="text-blue-500" />
                <div>
                  <span className="text-sm font-medium block">{file.name}</span>
                  <span className="text-xs text-gray-400">{file.size}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {/* لینک دانلود واقعی به سرور جنگو */}
                <a
                  href={file.url}
                  target="_blank"
                  rel="noreferrer"
                  className="p-2 text-gray-500 hover:text-blue-500 dark:hover:text-blue-400 transition-all"
                >
                  <Download size={18} />
                </a>
                <button
                  onClick={() => deleteFile(idx)}
                  className="p-2 text-gray-500 hover:text-red-500 transition-all"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

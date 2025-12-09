'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { removeToken } from '@/lib/auth';
import { LogOut, BarChart3 } from 'lucide-react';

export default function Navbar() {
  const router = useRouter();

  const handleLogout = () => {
    removeToken();
    router.push('/login');
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <BarChart3 className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">AdVision AI</span>
            </Link>
            <div className="ml-10 flex space-x-4">
              <Link
                href="/dashboard"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Dashboard
              </Link>
              <Link
                href="/campaigns"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Campaigns
              </Link>
              <Link
                href="/documents"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Documents
              </Link>
              <Link
                href="/chat"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                AI Chat
              </Link>
            </div>
          </div>
          <div className="flex items-center">
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 text-gray-700 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { documentsAPI } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';
import { Upload, FileText, Trash2, Search } from 'lucide-react';

interface Document {
  id: number;
  title: string;
  content: string;
  document_type: string;
  created_at: string;
}

interface QueryResult {
  content: string;
  metadata: any;
  relevance_score: number;
  document_id: string;
}

export default function DocumentsPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [query, setQuery] = useState('');
  const [queryResults, setQueryResults] = useState<QueryResult[]>([]);
  const [querying, setQuerying] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    fetchDocuments();
  }, [router]);

  const fetchDocuments = async () => {
    try {
      const response = await documentsAPI.list();
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await documentsAPI.upload(file);
      fetchDocuments();
      e.target.value = '';
    } catch (error) {
      console.error('Failed to upload document:', error);
      alert('Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      await documentsAPI.delete(id);
      fetchDocuments();
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;
    
    setQuerying(true);
    try {
      const response = await documentsAPI.query(query);
      setQueryResults(response.data.results);
    } catch (error) {
      console.error('Failed to query documents:', error);
    } finally {
      setQuerying(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
            <p className="text-gray-600 mt-1">Upload documents for AI-powered Q&A</p>
          </div>
          <label className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 cursor-pointer">
            <Upload className="h-5 w-5" />
            <span>{uploading ? 'Uploading...' : 'Upload Document'}</span>
            <input
              type="file"
              accept=".txt,.md,.pdf"
              onChange={handleUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
        </div>

        {/* Query Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Ask Questions</h2>
          <div className="flex space-x-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
              placeholder="Ask a question about your documents..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={handleQuery}
              disabled={querying || !query.trim()}
              className="flex items-center space-x-2 bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              <Search className="h-5 w-5" />
              <span>{querying ? 'Searching...' : 'Search'}</span>
            </button>
          </div>

          {/* Query Results */}
          {queryResults.length > 0 && (
            <div className="mt-6 space-y-4">
              <h3 className="font-semibold text-gray-900">Results:</h3>
              {queryResults.map((result, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-sm font-medium text-primary-600">
                      {result.metadata.title || 'Document'}
                    </span>
                    <span className="text-sm text-gray-500">
                      Relevance: {(result.relevance_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm">{result.content.substring(0, 300)}...</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Documents List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Your Documents</h2>
          </div>
          
          {documents.length === 0 ? (
            <div className="p-12 text-center">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No documents yet. Upload your first document!</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {documents.map((doc) => (
                <div key={doc.id} className="px-6 py-4 flex justify-between items-center hover:bg-gray-50">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900">{doc.title}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="text-red-600 hover:text-red-700 p-2"
                    title="Delete"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

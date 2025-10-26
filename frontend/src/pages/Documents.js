import React, { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useDropzone } from 'react-dropzone';
import { 
  FiUpload, 
  FiFile, 
  FiFileText, 
  FiTrash2, 
  FiDownload,
  FiEye,
  FiCheckCircle,
  FiAlertCircle,
  FiClock
} from 'react-icons/fi';
import { useAppStore } from '../store/appStore';
import { documentAPI } from '../services/api';
import toast from 'react-hot-toast';

const Documents = () => {
  const { addDocument, setUploadProgress } = useAppStore();
  const [uploading, setUploading] = useState(false);
  const queryClient = useQueryClient();

  // Fetch documents
  const { data: documentsData, isLoading, error } = useQuery(
    'documents',
    async () => {
      try {
        const response = await documentAPI.getAll();
        return response.data || [];
      } catch (err) {
        console.error('Error fetching documents:', err);
        return [];
      }
    },
    { retry: 1 }
  );

  const documents = Array.isArray(documentsData) ? documentsData : [];

  // Upload mutation
  const uploadMutation = useMutation(
    async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await documentAPI.upload(formData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        toast.success('Document uploaded successfully!');
        queryClient.invalidateQueries('documents');
        setUploading(false);
      },
      onError: (error) => {
        toast.error('Failed to upload document');
        console.error('Upload error:', error);
        setUploading(false);
      }
    }
  );

  // Delete mutation
  const deleteMutation = useMutation(
    (id) => documentAPI.delete(id),
    {
      onSuccess: () => {
        toast.success('Document deleted successfully');
        queryClient.invalidateQueries('documents');
      },
      onError: () => {
        toast.error('Failed to delete document');
      }
    }
  );

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setUploading(true);
      uploadMutation.mutate(acceptedFiles[0]);
    }
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: false
  });

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(id);
    }
  };

  const getFileIcon = (filename) => {
    const ext = filename?.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FiFileText className="text-red-500" />;
    if (ext === 'xlsx' || ext === 'xls') return <FiFile className="text-green-500" />;
    if (ext === 'csv') return <FiFile className="text-blue-500" />;
    return <FiFile className="text-gray-500" />;
  };

  const getStatusIcon = (status) => {
    if (status === 'processed') return <FiCheckCircle className="text-green-500" />;
    if (status === 'processing') return <FiClock className="text-yellow-500 animate-spin" />;
    return <FiAlertCircle className="text-gray-500" />;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
        <p className="text-gray-600 mt-2">
          Upload and manage your financial documents
        </p>
      </div>

      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors mb-8 ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        <FiUpload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {uploading ? (
          <div>
            <p className="text-lg font-medium text-gray-900">Uploading...</p>
            <div className="mt-4 w-64 mx-auto h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-primary-500 animate-pulse" style={{ width: '50%' }}></div>
            </div>
          </div>
        ) : (
          <div>
            <p className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive
                ? 'Drop the file here'
                : 'Drag & drop a file here, or click to select'}
            </p>
            <p className="text-sm text-gray-600">
              Supported formats: PDF, Excel (.xlsx, .xls), CSV (max 50MB)
            </p>
          </div>
        )}
      </div>

      {/* Documents List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading documents...</p>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <FiAlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <p className="text-gray-900 font-medium">Failed to load documents</p>
          <p className="text-gray-600 mt-2">Please try again later</p>
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <FiFileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-gray-900 font-medium">No documents yet</p>
          <p className="text-gray-600 mt-2">Upload your first document to get started</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Uploaded
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center">
                        {getFileIcon(doc.filename)}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {doc.filename || 'Untitled'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {doc.file_type || 'Unknown type'}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatFileSize(doc.file_size)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(doc.status)}
                      <span className="ml-2 text-sm text-gray-900 capitalize">
                        {doc.status || 'pending'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-red-600 hover:text-red-900 ml-4"
                      title="Delete"
                    >
                      <FiTrash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Documents;

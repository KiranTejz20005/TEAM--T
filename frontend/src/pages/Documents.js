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
  const { data: documents, isLoading, error } = useQuery(
    'documents',
    () => documentAPI.getAll(),
    { retry: 1 }
  );

  // Upload mutation
  const uploadMutation = useMutation(
    async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      return documentAPI.upload(formData);
    },
    {
      onSuccess: (data) => {
        toast.success('Document uploaded successfully');
        queryClient.invalidateQueries('documents');
        addDocument(data);
      },
      onError: (error) => {
        toast.error('Failed to upload document');
        console.error('Upload error:', error);
      }
    }
  );

  // Delete mutation
  const deleteMutation = useMutation(
    async (id) => documentAPI.delete(id),
    {
      onSuccess: () => {
        toast.success('Document deleted successfully');
        queryClient.invalidateQueries('documents');
      },
      onError: (error) => {
        toast.error('Failed to delete document');
        console.error('Delete error:', error);
      }
    }
  );

  // Process mutation
  const processMutation = useMutation(
    async (id) => documentAPI.process(id),
    {
      onSuccess: () => {
        toast.success('Document processed successfully');
        queryClient.invalidateQueries('documents');
      },
      onError: (error) => {
        toast.error('Failed to process document');
        console.error('Process error:', error);
      }
    }
  );

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      await uploadMutation.mutateAsync(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
      setUploadProgress(0);
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
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024 // 50MB
  });

  const getFileIcon = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    switch (extension) {
      case 'pdf':
        return <FiFileText className="text-error-500" />;
      case 'xlsx':
      case 'xls':
        return <FiFile className="text-success-500" />;
      case 'csv':
        return <FiFile className="text-warning-500" />;
      default:
        return <FiFile className="text-gray-500" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processed':
        return <FiCheckCircle className="text-success-500" />;
      case 'processing':
        return <FiClock className="text-warning-500" />;
      case 'error':
        return <FiAlertCircle className="text-error-500" />;
      default:
        return <FiClock className="text-gray-500" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <FiAlertCircle size={48} className="text-error-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Documents</h3>
        <p className="text-gray-600">Failed to load documents. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600">Upload and manage your financial documents</p>
        </div>
        <div className="text-sm text-gray-500">
          {documents?.count || 0} documents
        </div>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 cursor-pointer ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} disabled={uploading} />
          <div className="flex flex-col items-center">
            <FiUpload size={48} className="text-gray-400 mb-4" />
            {uploading ? (
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto mb-4"></div>
                <p className="text-lg font-medium text-gray-900">Uploading...</p>
                <p className="text-gray-600">Please wait while your document is being processed</p>
              </div>
            ) : isDragActive ? (
              <div>
                <p className="text-lg font-medium text-primary-600">Drop the file here</p>
                <p className="text-gray-600">Release to upload</p>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium text-gray-900">Upload Financial Documents</p>
                <p className="text-gray-600 mb-4">
                  Drag and drop your PDF, Excel, or CSV files here, or click to browse
                </p>
                <div className="text-sm text-gray-500">
                  Supported formats: PDF, XLSX, XLS, CSV (Max 50MB)
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Your Documents</h2>
        </div>
        
        {documents?.documents?.length === 0 ? (
          <div className="text-center py-12">
            <FiFileText size={48} className="text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Documents Yet</h3>
            <p className="text-gray-600 mb-4">Upload your first financial document to get started</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {documents?.documents?.map((doc) => (
              <div key={doc.id} className="px-6 py-4 hover:bg-gray-50 transition-colors duration-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      {getFileIcon(doc.filename)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {doc.filename}
                      </h3>
                      <div className="flex items-center space-x-4 mt-1">
                        <span className="text-xs text-gray-500">
                          {formatFileSize(doc.file_size)}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatDate(doc.uploaded_at)}
                        </span>
                        <div className="flex items-center space-x-1">
                          {getStatusIcon(doc.status)}
                          <span className="text-xs text-gray-500 capitalize">
                            {doc.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => processMutation.mutate(doc.id)}
                      disabled={doc.status === 'processing' || doc.status === 'processed'}
                      className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Process Document"
                    >
                      <FiEye size={16} />
                    </button>
                    
                    <button
                      onClick={() => window.open(doc.file_url, '_blank')}
                      className="p-2 text-gray-400 hover:text-gray-600"
                      title="Download"
                    >
                      <FiDownload size={16} />
                    </button>
                    
                    <button
                      onClick={() => deleteMutation.mutate(doc.id)}
                      className="p-2 text-gray-400 hover:text-error-600"
                      title="Delete"
                    >
                      <FiTrash2 size={16} />
                    </button>
                  </div>
                </div>
                
                {doc.status === 'error' && doc.error_message && (
                  <div className="mt-2 p-2 bg-error-50 border border-error-200 rounded text-sm text-error-700">
                    {doc.error_message}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">💡 Tips for Better Results</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Upload clear, high-quality PDF documents for better text extraction</li>
          <li>• Use structured Excel files with clear headers for better data processing</li>
          <li>• Ensure financial documents contain standard accounting terms</li>
          <li>• Large files may take longer to process</li>
        </ul>
      </div>
    </div>
  );
};

export default Documents;

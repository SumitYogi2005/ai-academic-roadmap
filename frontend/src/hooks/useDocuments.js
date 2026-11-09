import { useMutation, useQuery } from '@tanstack/react-query';
import apiClient from '../lib/axios';

export function useUploadDocument() {
  return useMutation({
    mutationFn: async ({ file, courseName, examDate, onUploadProgress }) => {
      const formData = new FormData();
      formData.append('file', file);
      if (courseName) formData.append('course_name', courseName);
      if (examDate) formData.append('exam_date', examDate);

      const { data } = await apiClient.post('/api/v1/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress,
      });
      return data;
    },
  });
}

export function useDocumentStatus(documentId) {
  return useQuery({
    queryKey: ['documents', documentId, 'status'],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/documents/${documentId}/status`);
      return data;
    },
    enabled: !!documentId,
    refetchInterval: (data) => {
      if (data?.status === 'completed' || data?.status === 'failed') return false;
      return 2000;
    },
  });
}

export function useDocumentExtraction(documentId) {
  return useQuery({
    queryKey: ['documents', documentId, 'extraction'],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/documents/${documentId}/extraction`);
      return data;
    },
    enabled: !!documentId,
  });
}

export function useConfirmExtraction() {
  return useMutation({
    mutationFn: async ({ documentId, extraction }) => {
      const { data } = await apiClient.put(
        `/api/v1/documents/${documentId}/extraction`,
        extraction
      );
      return data;
    },
  });
}

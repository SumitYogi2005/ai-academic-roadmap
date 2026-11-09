import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../lib/axios';

export function useAnalytics() {
  return useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/analytics/summary');
      return data;
    },
  });
}

export function useUpdateNodeProgress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ nodeId, status }) => {
      const { data } = await apiClient.patch(`/api/v1/progress/nodes/${nodeId}`, { status });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });
}

export function useRoadmapProgress(roadmapId) {
  return useQuery({
    queryKey: ['progress', roadmapId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/progress/roadmaps/${roadmapId}`);
      return data;
    },
    enabled: !!roadmapId,
  });
}

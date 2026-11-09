import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../lib/axios';

export function usePlannerSessions(weekStart) {
  return useQuery({
    queryKey: ['planner', 'sessions', weekStart],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/planner/sessions', {
        params: { week_start: weekStart },
      });
      return data;
    },
  });
}

export function useGeneratePlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ roadmapId, targetDate, dailyHours }) => {
      const { data } = await apiClient.post('/api/v1/planner/generate', {
        roadmap_id: roadmapId,
        target_date: targetDate,
        daily_hours: dailyHours,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planner'] });
    },
  });
}

export function useUpdateSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ sessionId, status }) => {
      const { data } = await apiClient.patch(`/api/v1/planner/sessions/${sessionId}`, { status });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planner'] });
    },
  });
}

export function useTodaySessions() {
  return useQuery({
    queryKey: ['planner', 'today'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/planner/sessions/today');
      return data;
    },
  });
}

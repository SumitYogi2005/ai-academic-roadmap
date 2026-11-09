import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient from '../lib/axios';

export function useAIChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useMutation({
    mutationFn: async ({ message, nodeId, roadmapId }) => {
      const { data } = await apiClient.post('/api/v1/assistant/chat', {
        message,
        node_id: nodeId,
        roadmap_id: roadmapId,
        conversation: messages,
      });
      return data;
    },
    onMutate: ({ message }) => {
      setIsLoading(true);
      setMessages((prev) => [...prev, { role: 'user', content: message }]);
    },
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
      setIsLoading(false);
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
      setIsLoading(false);
    },
  });

  const clearMessages = () => setMessages([]);

  return { messages, isLoading, sendMessage, clearMessages };
}

export function useGenerateQuiz() {
  return useMutation({
    mutationFn: async ({ nodeId, questionCount = 5 }) => {
      const { data } = await apiClient.post('/api/v1/assistant/quiz', {
        node_id: nodeId,
        question_count: questionCount,
      });
      return data;
    },
  });
}

export function useGenerateNotes() {
  return useMutation({
    mutationFn: async ({ nodeId }) => {
      const { data } = await apiClient.post('/api/v1/assistant/notes', { node_id: nodeId });
      return data;
    },
  });
}

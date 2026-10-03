import axios, { AxiosError } from 'axios';
import type {
  HealthResponse,
  ModelInfoResponse,
  MetricsResponse,
  DatasetInfoResponse,
  DatasetClassesResponse,
  PredictionResponse,
  PredictionHistoryListResponse,
  PredictionHistoryItem,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

/**
 * Extracts clean user-friendly error message from Axios errors
 */
export const extractErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<any>;
    if (axiosErr.response?.data?.detail) {
      const detail = axiosErr.response.data.detail;
      if (typeof detail === 'string') return detail;
      if (detail.message) return detail.message;
    }
    if (axiosErr.code === 'ERR_NETWORK') {
      return 'Cannot connect to backend server. Make sure FastAPI is running on http://127.0.0.1:8000';
    }
    return axiosErr.message || 'An unexpected API error occurred.';
  }
  if (error instanceof Error) return error.message;
  return 'An unknown error occurred.';
};

export const apiService = {
  getHealth: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  getModelInfo: async (): Promise<ModelInfoResponse> => {
    const response = await apiClient.get<ModelInfoResponse>('/model/info');
    return response.data;
  },

  getModelMetrics: async (): Promise<MetricsResponse> => {
    const response = await apiClient.get<MetricsResponse>('/model/metrics');
    return response.data;
  },

  getDatasetInfo: async (): Promise<DatasetInfoResponse> => {
    const response = await apiClient.get<DatasetInfoResponse>('/dataset/info');
    return response.data;
  },

  getDatasetClasses: async (): Promise<DatasetClassesResponse> => {
    const response = await apiClient.get<DatasetClassesResponse>('/dataset/classes');
    return response.data;
  },

  predictImage: async (file: File): Promise<PredictionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<PredictionResponse>('/predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  predictGradCAM: async (file: File): Promise<PredictionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<PredictionResponse>('/predict/gradcam', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getPredictions: async (limit: number = 50, offset: number = 0): Promise<PredictionHistoryListResponse> => {
    const response = await apiClient.get<PredictionHistoryListResponse>('/predictions', {
      params: { limit, offset },
    });
    return response.data;
  },

  getPredictionById: async (predictionId: string): Promise<PredictionHistoryItem> => {
    const response = await apiClient.get<PredictionHistoryItem>(`/predictions/${predictionId}`);
    return response.data;
  },

  deletePrediction: async (predictionId: string): Promise<{ status: string; message: string }> => {
    const response = await apiClient.delete<{ status: string; message: string }>(`/predictions/${predictionId}`);
    return response.data;
  },
};

export default apiService;

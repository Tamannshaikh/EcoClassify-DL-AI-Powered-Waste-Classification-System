/**
 * TypeScript interface definitions matching backend FastAPI schemas.
 */

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_name: string;
  model_version: string;
  classes: string[];
}

export interface TrainingConfig {
  architecture?: string;
  batch_size?: number;
  epochs_completed?: number;
  fine_tuned?: boolean;
  optimizer?: string;
  learning_rate?: number;
  data_augmentation?: boolean;
}

export interface CpuInferenceBenchmark {
  avg_latency_ms?: number;
  average_inference_ms?: number;
  min_latency_ms?: number;
  min_inference_ms?: number;
  max_latency_ms?: number;
  max_inference_ms?: number;
  p95_latency_ms?: number;
  p95_inference_ms?: number;
  approx_fps?: number;
  test_runs?: number;
}

export interface ModelInfoResponse {
  model_name: string;
  model_architecture: string;
  framework: string;
  input_shape: number[];
  classes: string[];
  num_classes: number;
  total_parameters: number;
  test_accuracy: number;
  macro_precision: number;
  macro_recall: number;
  macro_f1: number;
  weighted_f1: number;
  training_config: TrainingConfig;
  cpu_inference_benchmark?: CpuInferenceBenchmark;
}

export interface PerClassMetric {
  precision: number;
  recall: number;
  f1_score: number;
  support: number;
}

export interface ModelComparisonItem {
  model_name: string;
  architecture: string;
  test_accuracy: number;
  macro_f1: number;
  weighted_f1: number;
  total_parameters: number;
  avg_inference_ms: number;
  selected_for_production: boolean;
}

export interface MetricsResponse {
  accuracy: number;
  macro_precision: number;
  macro_recall: number;
  macro_f1: number;
  weighted_f1: number;
  per_class: Record<string, PerClassMetric>;
  confusion_matrix: number[][];
  model_comparison?: {
    models?: ModelComparisonItem[];
    comparison_summary?: Record<string, any>;
  };
}

export interface PredictionResponse {
  prediction_id: string;
  filename: string;
  predicted_class: string;
  confidence: number;
  probabilities: Record<string, number>;
  inference_time_ms: number;
  model_version: string;
  image_url?: string;
  image_path?: string;
  gradcam_base64: string | null;
}

export interface PredictionHistoryItem {
  id: number;
  prediction_id: string;
  filename: string;
  original_filename: string;
  predicted_class: string;
  confidence: number;
  probabilities: Record<string, number>;
  inference_time_ms: number;
  model_version: string;
  gradcam_generated: boolean;
  image_url?: string;
  image_path?: string;
  created_at: string;
}

export interface PredictionHistoryListResponse {
  total: number;
  predictions: PredictionHistoryItem[];
}

export interface ClassDistributionItem {
  class_name: string;
  count: number;
  percentage: number;
}

export interface DatasetInfoResponse {
  dataset_name: string;
  total_images: number;
  classes: string[];
  class_distribution: ClassDistributionItem[];
  splits: {
    train: number;
    val: number;
    test: number;
    total: number;
  };
  dimensions: string;
}

export interface DatasetClassesResponse {
  classes: string[];
  counts: Record<string, number>;
  total: number;
}

export interface ApiErrorResponse {
  detail: {
    code: string;
    message: string;
    errors?: any[];
  };
}

# API Specification

Base URL:
`/api/v1`

## Health
### GET /health
Response:
```json
{"status":"ok","model_loaded":true,"model_version":"v1.0"}
```

## Model
### GET /model/info
Returns:
```json
{
  "model_name":"MobileNetV2",
  "version":"v1.0",
  "input_size":[224,224],
  "classes":["cardboard","glass","metal","paper","plastic","organic"]
}
```

### GET /model/metrics
Returns evaluation metrics and training history.

## Prediction
### POST /predict
Content-Type:
`multipart/form-data`

Field:
`file`

Response:
```json
{
  "prediction":"plastic",
  "confidence":0.964,
  "probabilities":{
    "cardboard":0.004,
    "glass":0.014,
    "metal":0.007,
    "paper":0.009,
    "plastic":0.964,
    "organic":0.002
  },
  "model_version":"v1.0"
}
```

### POST /predict/gradcam
Uploads image and returns prediction plus Grad-CAM image when enabled.

## History
### GET /predictions
Returns recent prediction history.

### GET /predictions/{id}
Returns a single prediction.

### DELETE /predictions/{id}
Deletes a history item if local persistence is enabled.

## Dataset
### GET /dataset/info
Returns dataset metadata.

### GET /dataset/classes
Returns class names and counts.

## Training (development only)
### POST /training/start
Starts a training job.

Request:
```json
{
  "architecture":"mobilenetv2",
  "epochs":20,
  "batch_size":16
}
```

This endpoint must be disabled or protected in a public deployment.

### GET /training/status/{job_id}
Returns training status.

## Error Format
```json
{
  "detail":{
    "code":"INVALID_IMAGE",
    "message":"Unsupported or unreadable image."
  }
}
```

HTTP:
200 success
400 invalid request
413 file too large
422 validation error
500 server/model error
503 model unavailable

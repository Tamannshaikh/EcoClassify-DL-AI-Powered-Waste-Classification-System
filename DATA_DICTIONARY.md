# Data Dictionary

## Dataset Image Record

| Field | Type | Description |
|---|---|---|
| image_path | string | Local path or dataset-relative path |
| class_name | categorical | Waste category |
| class_id | integer | Numeric encoded class |
| split | categorical | train / validation / test |
| width | integer | Original image width |
| height | integer | Original image height |
| file_size | integer | Image file size in bytes |

## Supported Classes

| class_id | class_name |
|---:|---|
| 0 | cardboard |
| 1 | glass |
| 2 | metal |
| 3 | paper |
| 4 | plastic |
| 5 | organic |

The actual class order must be saved in `class_names.json` and loaded during inference. Never assume class order from directory listing.

## Prediction Fields

| Field | Type | Description |
|---|---|---|
| filename | string | Uploaded image filename |
| predicted_class | string | Highest-probability class |
| confidence | float | Probability of predicted class |
| probabilities | JSON | Probability for every class |
| model_version | string | Model used |
| created_at | datetime | Prediction timestamp |

## Training Fields

| Field | Description |
|---|---|
| architecture | CNN or MobileNetV2 |
| input_size | Model image size |
| batch_size | Training batch size |
| epochs | Maximum epochs |
| learning_rate | Initial learning rate |
| optimizer | Adam recommended |
| loss | sparse_categorical_crossentropy or categorical_crossentropy |
| augmentation | Training augmentation configuration |

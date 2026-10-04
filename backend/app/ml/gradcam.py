"""
Grad-CAM (Gradient-weighted Class Activation Mapping) Explainability Module.
Generates heatmap overlays highlighting salient regions for classification.
"""
import base64
import io
import logging
from typing import Optional
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import tensorflow as tf

from backend.app.ml.preprocessing import preprocess_single_image_for_inference

logger = logging.getLogger(__name__)


def generate_gradcam_heatmap(
    model: tf.keras.Model,
    img_array: np.ndarray,
    pred_index: Optional[int] = None
) -> Optional[np.ndarray]:
    """
    Computes Grad-CAM heatmap for the last convolutional layer inside MobileNetV2.
    """
    try:
        # 1. Locate MobileNetV2 backbone and last conv layer (e.g. 'out_relu')
        backbone_layer = model.get_layer("mobilenetv2_1.00_224")
        last_conv = backbone_layer.get_layer("out_relu")

        # 2. Build sub-model for backbone feature extraction
        backbone_grad_model = tf.keras.Model(
            inputs=[backbone_layer.input],
            outputs=[last_conv.output, backbone_layer.output]
        )

        # 3. Pass input through initial layers before backbone (rescaling/augmentation)
        x = img_array
        for layer_name in ["aug_flip", "aug_rotation", "aug_zoom", "mobilenet_rescaling"]:
            try:
                x = model.get_layer(layer_name)(x, training=False)
            except Exception:
                pass

        # 4. Compute gradients with GradientTape
        with tf.GradientTape() as tape:
            conv_outputs, backbone_out = backbone_grad_model(x, training=False)
            
            # Pass through classification head
            try:
                h = model.get_layer("gap")(backbone_out, training=False)
                h = model.get_layer("dense1")(h, training=False)
                try:
                    h = model.get_layer("dropout1")(h, training=False)
                except Exception:
                    pass
                preds = model.get_layer("predictions")(h, training=False)
            except Exception:
                # Fallback for 6-class baseline architecture
                h = model.get_layer("gap")(backbone_out, training=False)
                h = model.get_layer("dropout1")(h, training=False)
                h = model.get_layer("dense1")(h, training=False)
                h = model.get_layer("dropout2")(h, training=False)
                preds = model.get_layer("predictions")(h, training=False)

            if pred_index is None:
                pred_index = int(tf.argmax(preds[0]))
            class_loss = preds[:, pred_index]

        # 5. Calculate channel-wise pooled gradients
        grads = tape.gradient(class_loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # 6. Weight conv outputs by gradients
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # 7. Apply ReLU and normalize
        heatmap = tf.maximum(heatmap, 0.0) / (tf.reduce_max(heatmap) + 1e-10)
        return heatmap.numpy()

    except Exception as e:
        logger.warning(f"Grad-CAM generation encountered an issue: {e}")
        return None


def create_gradcam_overlay(
    pil_image: Image.Image,
    model: tf.keras.Model,
    pred_index: Optional[int] = None,
    alpha: float = 0.45
) -> Optional[str]:
    """
    Generates Grad-CAM heatmap, overlays onto the original image,
    and returns a base64 encoded JPEG data URI.
    """
    try:
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        orig_w, orig_h = pil_image.size
        img_array = preprocess_single_image_for_inference(pil_image, model_type="mobilenetv2")

        heatmap = generate_gradcam_heatmap(model, img_array, pred_index=pred_index)
        if heatmap is None:
            return None

        # Resize heatmap to match original image dimensions
        heatmap_img = Image.fromarray(np.uint8(255 * heatmap))
        heatmap_img = heatmap_img.resize((orig_w, orig_h), Image.Resampling.BILINEAR)
        heatmap_np = np.array(heatmap_img) / 255.0

        # Apply Jet Colormap using matplotlib.pyplot.colormaps
        jet_cmap = plt.get_cmap("jet")
        jet_colors = jet_cmap(heatmap_np)[:, :, :3]  # Drop alpha
        jet_heatmap = np.uint8(255 * jet_colors)

        # Blend original with heatmap
        orig_np = np.array(pil_image)
        blended = np.uint8((1.0 - alpha) * orig_np + alpha * jet_heatmap)

        blended_pil = Image.fromarray(blended)
        buffered = io.BytesIO()
        blended_pil.save(buffered, format="JPEG", quality=90)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}"

    except Exception as e:
        logger.warning(f"Failed to create Grad-CAM overlay: {e}")
        return None

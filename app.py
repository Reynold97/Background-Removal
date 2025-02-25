import gradio as gr
from loadimg import load_img
from transformers import AutoModelForImageSegmentation
import torch
from torchvision import transforms

torch.set_float32_matmul_precision(["high", "highest"][0])

birefnet = AutoModelForImageSegmentation.from_pretrained(
    "ZhengPeng7/BiRefNet", trust_remote_code=True
)
birefnet.to("cuda")

transform_image = transforms.Compose(
    [
        transforms.Resize((1024, 1024)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)

def process_image(image):
    if image is None:
        return None
    
    try:
        im = load_img(image, output_type="pil")
        im = im.convert("RGB")
        
        # Process the image
        image_size = im.size
        input_images = transform_image(im).unsqueeze(0).to("cuda")
        
        # Prediction
        with torch.no_grad():
            preds = birefnet(input_images)[-1].sigmoid().cpu()
        pred = preds[0].squeeze()
        pred_pil = transforms.ToPILImage()(pred)
        mask = pred_pil.resize(image_size)
        
        # Apply alpha mask
        result = im.copy()
        result.putalpha(mask)
        
        return result
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

# Set app title
app_title = "Natasquad AI Background Removal Tool"
app_description = "Remove backgrounds from images with AI"

# CSS to hide the footer
css = """
footer {display: none !important;}
.gradio-container {min-height: 0 !important;}
"""

# Create Gradio app with a simplified layout
with gr.Blocks(title=app_title, css=css) as demo:
    gr.Markdown(f"# {app_title}")
    gr.Markdown(app_description)
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(label="Input Image", type="pil")
            process_btn = gr.Button("Remove Background", variant="primary")
        
        output_image = gr.Image(label="Result (Transparent Background)", type="pil")
    
    process_btn.click(fn=process_image, inputs=input_image, outputs=output_image)

if __name__ == "__main__":
    # Launch with customized parameters
    demo.launch(show_error=True, server_port=8080, show_api=False, server_name="0.0.0.0")
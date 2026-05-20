from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
import torch
from flask import Flask, request, jsonify

app = Flask(__name__)


MODEL_PATH = "zai-org/GLM-OCR"
print(f"Loading model {MODEL_PATH}...")

processor = AutoProcessor.from_pretrained(MODEL_PATH)
model = AutoModelForImageTextToText.from_pretrained(
    pretrained_model_name_or_path=MODEL_PATH,
    dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto",
)

print("Model Loaded!")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "Text Recognition:"}
        ]
    }
]

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    PROMPT = processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    
    file = request.files["image"]

    try:
        image = Image.open(file.stream).convert("RGB")

        inputs = processor(images=image, text=PROMPT, return_tensors="pt").to(model.device)

        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=1024,
                do_sample=False,
                use_cache=True
            )
        
        output_text = processor.decode(
            output[0][inputs["input_ids"].shape[1]:], 
            skip_special_tokens=False
        )

        return jsonify({"result": output_text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7777)
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image

def load_qwen2_vl_model():
    """
    Load Qwen2-VL model and tokenizer
    """
    model_id = "Qwen/Qwen2-VL-7B"
    
    # Load model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        device_map="auto",  # Automatic device placement
        torch_dtype=torch.float16,  # Use float16 for memory efficiency
        trust_remote_code=True,
        use_auth_token = "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"
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        model_id, 
        trust_remote_code=True
    )
    
    return model, tokenizer

def load_llama3_vision_model():
    """
    Load Llama 3.2 Vision model and tokenizer
    """
    model_id = "meta-llama/Meta-Llama-3-Vision"
    
    # Load model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
        use_auth_token = "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"
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        trust_remote_code=True
    )
    
    return model, tokenizer

def process_image_with_qwen2_vl(model, tokenizer, image_path, prompt):
    """
    Process an image using Qwen2-VL model
    
    Args:
        model: Loaded Qwen2-VL model
        tokenizer: Loaded Qwen2-VL tokenizer
        image_path: Path to the image file
        prompt: Text prompt for image analysis
    
    Returns:
        Generated text response
    """
    # Open and prepare the image
    image = Image.open(image_path).convert('RGB')
    
    # Prepare inputs
    inputs = tokenizer.from_list_images([image], prompt)
    
    # Generate response
    generate_ids = model.generate(
        **inputs, 
        max_new_tokens=128,  # Adjust as needed
        do_sample=True
    )
    
    # Decode the response
    response = tokenizer.decode(generate_ids[0])
    return response

def process_image_with_llama3_vision(model, tokenizer, image_path, prompt):
    """
    Process an image using Llama 3.2 Vision model
    
    Args:
        model: Loaded Llama 3.2 Vision model
        tokenizer: Loaded Llama 3.2 Vision tokenizer
        image_path: Path to the image file
        prompt: Text prompt for image analysis
    
    Returns:
        Generated text response
    """
    # Open and prepare the image
    image = Image.open(image_path).convert('RGB')
    
    # Prepare inputs
    inputs = tokenizer(
        prompt,
        images=image,
        return_tensors="pt",
        padding=True
    )
    
    # Generate response
    generate_ids = model.generate(
        **inputs, 
        max_new_tokens=128,  # Adjust as needed
        do_sample=True
    )
    
    # Decode the response
    response = tokenizer.decode(generate_ids[0], skip_special_tokens=True)
    return response

def main():
    # Example usage
    image_path = r"C:\Users\Admin\Pictures\Screenshots\Screenshot 2024-11-20 185447.png"
    prompt = "Describe what you see in this image"
    
    # Qwen2-VL Processing
    qwen_model, qwen_tokenizer = load_qwen2_vl_model()
    qwen_response = process_image_with_qwen2_vl(
        qwen_model, 
        qwen_tokenizer, 
        image_path, 
        prompt
    )
    print("Qwen2-VL Response:", qwen_response)
    
    # Llama 3.2 Vision Processing
    llama_model, llama_tokenizer = load_llama3_vision_model()
    llama_response = process_image_with_llama3_vision(
        llama_model, 
        llama_tokenizer, 
        image_path, 
        prompt
    )
    print("Llama 3.2 Vision Response:", llama_response)

if __name__ == "__main__":
    main()
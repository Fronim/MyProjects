import os
import torch
from PIL import Image
from facenet_pytorch import MTCNN
from torchvision import transforms
from tqdm import tqdm


def process_directory(input_dir, output_dir, mtcnn):
    os.makedirs(output_dir, exist_ok=True)
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    print(f"Processing {len(image_files)} images from {input_dir}...")

    for filename in tqdm(image_files, desc=f"Cropping {os.path.basename(input_dir)}"):
        img_path = os.path.join(input_dir, filename)
        save_path = os.path.join(output_dir, filename)

        if os.path.exists(save_path):
            continue

        try:
            image = Image.open(img_path).convert('RGB')
            boxes, _ = mtcnn.detect(image)

            if boxes is not None:
                box = boxes[0]
                face_img = image.crop((int(box[0]), int(box[1]), int(box[2]), int(box[3])))
            else:
                face_img = transforms.CenterCrop(400)(image)

            face_img.save(save_path)

        except Exception as e:
            print(f"\nError processing {filename}: {e}")


if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    mtcnn = MTCNN(keep_all=False, select_largest=True, device=device)

    base_dir = "data"

    train_in = os.path.join(base_dir, "train")
    train_out = os.path.join(base_dir, "train_faces")

    test_in = os.path.join(base_dir, "test")
    test_out = os.path.join(base_dir, "test_faces")

    process_directory(train_in, train_out, mtcnn)
    if os.path.exists(test_in):
        process_directory(test_in, test_out, mtcnn)

    print("\nPre-processing complete!")
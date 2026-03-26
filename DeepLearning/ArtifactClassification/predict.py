import os
import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader
from sklearn.metrics import f1_score, classification_report
from tqdm import tqdm

from train import ArtifactDataset, GlobalViT, LocalCNN


def run_final_validation(test_dir, faces_dir, vit_path, cnn_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Loading ensemble models...")
    model_g = GlobalViT().to(device)
    model_g.load_state_dict(torch.load(vit_path, map_location=device))
    model_g.eval()

    model_l = LocalCNN().to(device)
    model_l.load_state_dict(torch.load(cnn_path, map_location=device))
    model_l.eval()

    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    global_val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        normalize
    ])

    face_val_transform = transforms.Compose([
        transforms.Resize((288, 288)),
        transforms.ToTensor(),
        normalize
    ])


    test_dataset = ArtifactDataset(
        test_dir,
        faces_dir,
        global_val_transform,
        face_val_transform
    )
    test_loader = DataLoader(test_dataset, batch_size=16)

    all_preds = []
    all_targets = []

    print(f"Validating High-Res Ensemble on {len(test_dataset)} UNSEEN images...")
    with torch.no_grad():
        for global_img, local_img, targets in tqdm(test_loader):
            global_img, local_img = global_img.to(device), local_img.to(device)

            out_g = model_g(global_img).squeeze()
            out_l = model_l(local_img).squeeze()

            if out_g.dim() == 0: out_g = out_g.unsqueeze(0)
            if out_l.dim() == 0: out_l = out_l.unsqueeze(0)

            prob_g = torch.sigmoid(out_g)
            prob_l = torch.sigmoid(out_l)

            avg_prob = (0.2 * prob_g) + (0.8 * prob_l)
            preds = (avg_prob > 0.5).float()

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())

    final_f1 = f1_score(all_targets, all_preds, average='macro')

    print("\n" + "=" * 40)
    print("FINAL VALIDATION RESULTS")
    print("=" * 40)
    print(f"Macro F1 Score: {final_f1:.4f}")
    print("-" * 40)
    print(classification_report(all_targets, all_preds, target_names=['Artifact', 'Clean']))
    print("=" * 40)


if __name__ == "__main__":
    run_final_validation(
        test_dir="data/test",
        faces_dir="data/test_faces",
        vit_path="global_vit_better_recall.pth",
        cnn_path="local_cnn_better_recall.pth"
    )
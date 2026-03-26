import os
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from tqdm import tqdm
import torch.nn.functional as F


class BinaryFocalLoss(nn.Module):
    def __init__(self, gamma=2.0, pos_weight=None):
        super(BinaryFocalLoss, self).__init__()
        self.gamma = gamma
        self.pos_weight = pos_weight

    def forward(self, logits, targets):
        bce_loss = F.binary_cross_entropy_with_logits(
            logits, targets, reduction='none', pos_weight=self.pos_weight
        )

        probs = torch.sigmoid(logits)
        p_t = probs * targets + (1 - probs) * (1 - targets)

        modulating_factor = (1.0 - p_t) ** self.gamma
        focal_loss = modulating_factor * bce_loss

        return focal_loss.mean()


class ArtifactDataset(Dataset):
    def __init__(self, global_dir, local_dir, global_transform, local_transform):
        self.global_dir = global_dir
        self.local_dir = local_dir
        self.global_transform = global_transform
        self.local_transform = local_transform
        self.filenames = [f for f in os.listdir(global_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        filename = self.filenames[idx]
        label = int(filename.split('_')[-1].split('.')[0])

        global_path = os.path.join(self.global_dir, filename)
        global_img = Image.open(global_path).convert('RGB')
        global_tensor = self.global_transform(global_img)

        local_path = os.path.join(self.local_dir, filename)
        local_img = Image.open(local_path).convert('RGB')
        local_tensor = self.local_transform(local_img)

        return global_tensor, local_tensor, torch.tensor(label, dtype=torch.float32)


class GlobalViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = models.vit_b_16(weights=models.ViT_B_16_Weights.DEFAULT)
        self.vit.heads = nn.Linear(768, 1)

    def forward(self, x):
        return self.vit(x)


class LocalCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
        self.cnn.classifier[1] = nn.Linear(1280, 1)

    def forward(self, x):
        return self.cnn(x)


def train(model_g, model_l, train_loader, criterion, opt_g, opt_l, epochs, device):
    print(f"Starting Training for {epochs} epochs...")

    for epoch in range(epochs):
        model_g.train()
        model_l.train()
        running_loss = 0.0

        loop = tqdm(train_loader, desc=f"Epoch [{epoch + 1}/{epochs}]", leave=True)
        for global_img, local_img, targets in loop:
            global_img, local_img, targets = global_img.to(device), local_img.to(device), targets.to(device)

            out_g = model_g(global_img).squeeze()
            out_l = model_l(local_img).squeeze()

            if out_g.dim() == 0: out_g = out_g.unsqueeze(0)
            if out_l.dim() == 0: out_l = out_l.unsqueeze(0)

            loss_g = criterion(out_g, targets)
            loss_l = criterion(out_l, targets)

            total_loss = loss_g + loss_l

            opt_g.zero_grad()
            opt_l.zero_grad()

            loss_g.backward()
            loss_l.backward()

            opt_g.step()
            opt_l.step()

            running_loss += total_loss.item()
            loop.set_postfix(loss=total_loss.item())

        avg_train_loss = running_loss / len(train_loader)
        print(f"End of Epoch {epoch + 1} | Train Loss: {avg_train_loss:.4f}")

    torch.save(model_g.state_dict(), "global_vit.pth")
    torch.save(model_l.state_dict(), "local_cnn.pth")
    print("Training complete! Final ensemble weights saved.")


if __name__ == "__main__":
    EPOCHS = 8
    BATCH_SIZE = 16
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running on {DEVICE}")

    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    global_train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.RandomAffine(degrees=3, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        transforms.RandomApply([transforms.GaussianBlur(kernel_size=3)], p=0.2),
        transforms.ToTensor(),
        normalize
    ])

    face_train_transform = transforms.Compose([
        transforms.Resize((224, 224)), # 288, 288
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.RandomAffine(degrees=3, translate=(0.02, 0.02), scale=(0.98, 1.02)),
        transforms.ToTensor(),
        transforms.RandomErasing(p=0.3, scale=(0.02, 0.15), ratio=(0.3, 3.3), value=0),
        normalize
    ])

    train_dataset = ArtifactDataset(
        global_dir="data/train",
        local_dir="data/train_faces",
        global_transform=global_train_transform,
        local_transform=face_train_transform
    )

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    labels = [int(f.split('_')[-1].split('.')[0]) for f in train_dataset.filenames]
    num_ones = sum(labels)
    num_zeros = len(labels) - num_ones
    pos_weight = torch.tensor([num_zeros / num_ones if num_ones > 0 else 1.0]).to(DEVICE)

    model_g = GlobalViT().to(DEVICE)
    model_l = LocalCNN().to(DEVICE)

    criterion = BinaryFocalLoss(gamma=2.0, pos_weight=pos_weight)

    opt_g = torch.optim.AdamW(model_g.parameters(), lr=1e-4, weight_decay=1e-2)
    opt_l = torch.optim.AdamW(model_l.parameters(), lr=1e-4, weight_decay=1e-2)

    train(model_g, model_l, train_loader, criterion, opt_g, opt_l, EPOCHS, DEVICE)
"""
Training scaffold for ManipulationCNN (ai/models/cnn_classifier.py).

This is NOT run automatically by the application — it's provided so the
project can genuinely be extended into a trained model, per the "Future
Scope" section of the report.

Expected dataset layout:

    dataset/
        genuine/  *.png|jpg  (authentic, unedited screenshots)
        manipulated/ *.png|jpg  (screenshots with known edits)

Usage:
    python train.py --data-dir ./dataset --epochs 15 --out ./weights/cnn_weights.pt
"""
from __future__ import annotations

import argparse
import os

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image

from cnn_classifier import ManipulationCNN


class ScreenshotDataset(Dataset):
    def __init__(self, root: str, transform):
        self.samples: list[tuple[str, int]] = []
        for label, sub in enumerate(["genuine", "manipulated"]):
            folder = os.path.join(root, sub)
            if not os.path.isdir(folder):
                continue
            for fname in os.listdir(folder):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    self.samples.append((os.path.join(folder, fname), label))
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        return self.transform(img), torch.tensor([float(label)])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--out", default="./weights/cnn_weights.pt")
    args = parser.parse_args()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    dataset = ScreenshotDataset(args.data_dir, transform)
    if len(dataset) == 0:
        raise SystemExit("No training images found — populate dataset/genuine and dataset/manipulated first.")
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model = ManipulationCNN()
    model.net.train()
    optimizer = torch.optim.Adam(model.net.parameters(), lr=args.lr)
    criterion = nn.BCELoss()

    for epoch in range(args.epochs):
        total_loss = 0.0
        for images, labels in loader:
            optimizer.zero_grad()
            outputs = model.net(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch + 1}/{args.epochs} - loss: {total_loss / len(loader):.4f}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    torch.save(model.net.state_dict(), args.out)
    print(f"Saved trained weights to {args.out}")


if __name__ == "__main__":
    main()

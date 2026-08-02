# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import logging

import modal
import torch
import torch.nn as nn
import torch.optim as optim

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("camelot_modal_sky")

app = modal.App("camelot_modal_sky")

# 1. Define the Container Image
image = modal.Image.debian_slim().pip_install("torch", "numpy")


# 2. Define the Model (The Logic from the prompt)
class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(28 * 28, 10)  # Simple linear model for digits (MNIST style)

    def forward(self, x):
        return self.fc(x)


# 3. The Function (Running on Sky GPU)
@app.function(image=image, gpu="any")
def train_model_step(data_batch, label_batch):
    logger.info("SKY: Received training batch — engaging GPU")

    model = SimpleNet().cuda()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01)

    # Fake Data for simulation since we don't have the dataset uploaded yet
    # In a real scenario, we'd mount a Volume
    inputs = torch.randn(64, 28 * 28).cuda()
    labels = torch.randint(0, 10, (64,)).cuda()

    outputs = model(inputs)
    loss = criterion(outputs, labels)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return float(loss.item())


# 4. The Web Endpoint (The Bridge from React)
@app.function(image=image)
@modal.web_endpoint(method="POST")
def agent_dispatch(item: dict):
    logger.info(f"GATEWAY: Received intent={item.get('intent')}")
    prompt = item.get("intent", "")

    if "TRAIN" in prompt.upper() or "MODEL" in prompt.upper():
        loss = train_model_step.remote([], [])
        return {"response": f"Training Step Complete. Loss: {loss:.4f} (Calculated on NVIDIA Cloud GPU)"}

    if "DEBATE" in prompt.upper():
        return {"response": "MERLIN: Separation is Order. ANYA: Latency is Death. MORGANA: Chaos is Truth."}

    return {"response": f"Basic Logic Executed. You said: {prompt}"}
from typing import Optional

import timm
import torch
import torch.nn as nn
from pytorch_lightning import LightningModule
from torchmetrics import Accuracy


OPT = "adam"  # adam, sgd
WEIGHT_DECAY = 0.0001
MOMENTUM = 0.9  # only when OPT is sgd
BASE_LR = 0.001
LR_SCHEDULER = "step"  # step, multistep, reduce_on_plateau
LR_DECAY_RATE = 0.1
LR_STEP_SIZE = 5  # only when LR_SCHEDULER is step
LR_STEP_MILESTONES = [10, 15]  # only when LR_SCHEDULER is multistep


def get_optimizer(parameters) -> torch.optim.Optimizer:
    if OPT == "adam":
        optimizer = torch.optim.Adam(parameters, lr=BASE_LR, weight_decay=WEIGHT_DECAY)
    elif OPT == "sgd":
        optimizer = torch.optim.SGD(
            parameters, lr=BASE_LR, weight_decay=WEIGHT_DECAY, momentum=MOMENTUM
        )
    else:
        raise NotImplementedError()

    return optimizer


def get_lr_scheduler_config(optimizer: torch.optim.Optimizer) -> dict:
    if LR_SCHEDULER == "step":
        scheduler = torch.optim.lr_scheduler.StepLR(
            optimizer, step_size=LR_STEP_SIZE, gamma=LR_DECAY_RATE
        )
        lr_scheduler_config = {
            "scheduler": scheduler,
            "interval": "epoch",
            "frequency": 1,
        }
    elif LR_SCHEDULER == "multistep":
        scheduler = torch.optim.lr_scheduler.MultiStepLR(
            optimizer, milestones=LR_STEP_MILESTONES, gamma=LR_DECAY_RATE
        )
        lr_scheduler_config = {
            "scheduler": scheduler,
            "interval": "epoch",
            "frequency": 1,
        }
    elif LR_SCHEDULER == "reduce_on_plateau":
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="max", factor=0.1, patience=10, threshold=0.0001
        )
        lr_scheduler_config = {
            "scheduler": scheduler,
            "monitor": "val/loss",
            "interval": "epoch",
            "frequency": 1,
        }
    else:
        raise NotImplementedError

    return lr_scheduler_config


class ModelInference(LightningModule):
    def __init__(
        self,
        model_name: str = "resnet50",
        pretrained: bool = False,
        num_classes: Optional[int] = None,
    ):
        super().__init__()
        self.save_hyperparameters()
        self.model = timm.create_model(
            model_name=model_name,
            pretrained=pretrained,
            num_classes=num_classes,
            drop_rate=0.5,
        )
        self.train_loss = nn.CrossEntropyLoss()
        self.train_acc = Accuracy(task="multiclass", num_classes=num_classes)
        self.val_loss = nn.CrossEntropyLoss()
        self.val_acc = Accuracy(task="multiclass", num_classes=num_classes)

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, target = batch

        out = self(x)
        _, pred = out.max(1)

        loss = self.train_loss(out, target)
        acc = self.train_acc(pred, target)
        self.log_dict({"train/loss": loss, "train/acc": acc}, prog_bar=True)

        return loss

    def validation_step(self, batch, batch_idx):
        x, target = batch

        out = self(x)
        _, pred = out.max(1)

        loss = self.val_loss(out, target)
        acc = self.val_acc(pred, target)
        self.log_dict({"val/loss": loss, "val/acc": acc})

    def configure_optimizers(self):
        optimizer = get_optimizer(self.parameters())
        lr_scheduler_config = get_lr_scheduler_config(optimizer)
        return {"optimizer": optimizer, "lr_scheduler": lr_scheduler_config}

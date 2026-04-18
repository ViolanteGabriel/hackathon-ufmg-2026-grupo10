import torch
import torch.nn as nn
import torch.nn.functional as F

class LitigationModel(nn.Module):
    """
    Neural Network for deciding between Defense or Agreement.
    Focuses on predicting the probability of victory or loss.
    """
    def __init__(self, input_dim, hidden_dims=[128, 64, 32], dropout_rate=0.2):
        super(LitigationModel, self).__init__()
        
        # Shared Layers (Feature Extraction)
        layers = []
        last_dim = input_dim
        for h_dim in hidden_dims:
            layers.append(nn.Linear(last_dim, h_dim))
            layers.append(nn.ReLU())
            layers.append(nn.BatchNorm1d(h_dim))
            layers.append(nn.Dropout(dropout_rate))
            last_dim = h_dim
        
        self.shared_backbone = nn.Sequential(*layers)
        
        # Classifier Head: Outcome Classification (0: VITORIA/IMPROCEDENTE, 1: PERDA/PARCIAL OU PROCEDENTE)
        self.classifier_head = nn.Sequential(
            nn.Linear(last_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 2) # 2 classes: Win or Loss
        )

    def forward(self, x):
        features = self.shared_backbone(x)
        logits = self.classifier_head(features)
        return logits

def calculate_loss(logits, target_class):
    """
    Standard CrossEntropy loss for classification.
    """
    return F.cross_entropy(logits, target_class)

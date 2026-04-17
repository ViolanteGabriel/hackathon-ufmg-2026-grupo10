import torch
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
import pandas as pd
import numpy as np
import os

from model import LitigationModel
from dataset import LitigationDataset

def train_model(epochs=30, batch_size=64, lr=0.001):
    # 1. Prepare Data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resultados_path = os.path.join(current_dir, "resultados_dos_processos.csv")
    subsidios_path = os.path.join(current_dir, "subsidios_disponibilizados.csv")
        
    print(f"Loading data from {resultados_path} and {subsidios_path}...")
    if not os.path.exists(resultados_path):
        # Fallback to sentencas.csv if main files are missing
        resultados_path = os.path.join(current_dir, "sentencas.csv")
        if not os.path.exists(resultados_path):
            raise FileNotFoundError(f"Required CSV files not found.")
        df_merged = pd.read_csv(resultados_path)
    else:
        df_res = pd.read_csv(resultados_path)
        if os.path.exists(subsidios_path):
            df_sub = pd.read_csv(subsidios_path)
            # Merge on process number. Note the typo 'processos' in subsidios file
            merge_col_res = 'Número do processo'
            merge_col_sub = 'Número do processos' if 'Número do processos' in df_sub.columns else 'Número do processo'
            
            df_merged = pd.merge(df_res, df_sub, left_on=merge_col_res, right_on=merge_col_sub, how='left')
            # Drop the redundant column if name was different
            if merge_col_res != merge_col_sub:
                df_merged = df_merged.drop(columns=[merge_col_sub])
        else:
            df_merged = df_res
        
    dataset = LitigationDataset(dataframe=df_merged)
    
    train_size = int(0.7 * len(dataset))
    val_size = int(0.15 * len(dataset))
    test_size = len(dataset) - train_size - val_size
    train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    # 2. Initialize Model
    input_dim = len(dataset.feature_cols)
    model = LitigationModel(input_dim=input_dim)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # Max value for normalization (to keep loss scales comparable)
    max_val = dataset.df[dataset.target_value_col].max()
    if pd.isna(max_val) or max_val == 0: max_val = 1.0
    
    # 3. Training Loop
    print(f"Starting training for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for x, y_class, y_val in train_loader:
            optimizer.zero_grad()
            
            logits, pred_val = model(x)
            
            # Loss calculation
            class_loss = torch.nn.functional.cross_entropy(logits, y_class)
            reg_loss = torch.nn.functional.mse_loss(pred_val.squeeze(), y_val)
            
            # Weighted loss
            loss = 0.5 * class_loss + 0.5 * (reg_loss / (max_val**2 + 1e-6))
            
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            
        if (epoch + 1) % 5 == 0 or epoch == 0:
            # Validation step
            model.eval()
            val_loss = 0
            with torch.no_grad():
                for vx, vy_class, vy_val in val_loader:
                    v_logits, v_pred_val = model(vx)
                    v_class_loss = torch.nn.functional.cross_entropy(v_logits, vy_class)
                    v_reg_loss = torch.nn.functional.mse_loss(v_pred_val.squeeze(), vy_val)
                    v_loss = 0.5 * v_class_loss + 0.5 * (v_reg_loss / (max_val**2 + 1e-6))
                    val_loss += v_loss.item()
            
            print(f"Epoch {epoch+1}/{epochs}, Train Loss: {train_loss/len(train_loader):.4f}, Val Loss: {val_loss/len(val_loader):.4f}")
            
    # 4. Evaluation & Decision Logic (Final Test Set)
    model.eval()
    print("\nTesting decision logic on TEST set...")
    with torch.no_grad():
        correct_decisions = 0
        total = 0
        test_loss = 0
        for x, y_class, y_val in test_loader:
            logits, pred_val = model(x)
            probs = torch.nn.functional.softmax(logits, dim=1)
            
            # Expected Loss = (1 - P(Improcedente)) * Predicted_Value
            p_win = probs[:, 0]
            expected_loss = (1 - p_win) * pred_val.squeeze()
            
            # Recover 'valor_causa' from normalized features
            # 'Valor da causa' is index 3 in feature_cols
            idx_causa = dataset.feature_cols.index('Valor da causa')
            valor_causa = x[:, idx_causa] * dataset.scaler.scale_[idx_causa] + dataset.scaler.mean_[idx_causa]
            
            # Agreement Value heuristic: 40% of the 'valor_causa'
            agreement_cost = valor_causa * 0.4 
            
            decision = (expected_loss > agreement_cost).long() # 1 for Agreement, 0 for Defense
            
            # Actual decision comparison: did the actual outcome cost more than our agreement threshold?
            actual_loss_is_high = (y_val > agreement_cost).long()
            correct_decisions += (decision == actual_loss_is_high).sum().item()
            total += y_class.size(0)
            
    print(f"Decision Accuracy on TEST set (Agreement vs Defense): {correct_decisions/total:.2%}")
    
    # 5. Save Model
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
    models_dir = os.path.join(root_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "litigation_model.pth")
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()

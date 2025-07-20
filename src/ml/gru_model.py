import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import mlflow
import mlflow.pytorch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
import warnings
import logging
from datetime import datetime
warnings.filterwarnings('ignore')

# Configure MLflow logging to reduce warnings
logging.getLogger("mlflow").setLevel(logging.ERROR)

class GRUPairsModel(nn.Module):
    """
    PyTorch GRU model that replicates the exact TensorFlow architecture
    from the existing implementation with F1=0.7445 performance.
    """
    
    def __init__(self, input_size=10, hidden_size=128, num_layers=2, dropout=0.255):
        super(GRUPairsModel, self).__init__()
        
        # Replicate exact TensorFlow architecture
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # First GRU layer (128 units)
        self.gru1 = nn.GRU(input_size, hidden_size, num_layers=1, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        
        # Second GRU layer (64 units)
        self.gru2 = nn.GRU(hidden_size, hidden_size//2, num_layers=1, batch_first=True)
        
        # Final dense layer
        self.fc = nn.Linear(hidden_size//2, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        # Replicate exact TensorFlow forward pass
        # x shape: (batch_size, sequence_length, input_size)
        
        # First GRU layer
        gru1_out, _ = self.gru1(x)
        gru1_out = self.dropout(gru1_out)
        
        # Second GRU layer (only use last output)
        gru2_out, _ = self.gru2(gru1_out)
        last_output = gru2_out[:, -1, :]  # Take last timestep
        
        # Final dense layer
        output = self.fc(last_output)
        output = self.sigmoid(output)
        
        return output

class PairsDataset(Dataset):
    """
    PyTorch Dataset for pairs trading data with sequence creation.
    """
    
    def __init__(self, features, targets, sequence_length=10):
        # Handle both 2D (reshaped) and 3D (sequence) data
        if hasattr(features, 'values'):
            # DataFrame input - create sequences
            self.features = torch.FloatTensor(features.values)
            self.targets = torch.FloatTensor(targets.values)
            self.sequence_length = sequence_length
            self.use_sequences = False
        else:
            # Numpy array input - already in sequence format
            self.features = torch.FloatTensor(features)
            self.targets = torch.FloatTensor(targets)
            self.sequence_length = sequence_length
            self.use_sequences = True
        
    def __len__(self):
        if self.use_sequences:
            return len(self.features)
        else:
            return len(self.features) - self.sequence_length
        
    def __getitem__(self, idx):
        if self.use_sequences:
            # Data is already in sequence format
            x = self.features[idx]
            y = self.targets[idx]
        else:
            # Create sequence from 2D data
            x = self.features[idx:idx + self.sequence_length]
            y = self.targets[idx + self.sequence_length]
        return x, y

class GRUTrainer:
    """
    Training utilities for GRU model with MLflow integration.
    """
    
    def __init__(self, model, train_loader, val_loader, config):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        
        # Optimizer (same as TensorFlow)
        self.optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'])
        
        # Loss function
        self.criterion = nn.BCELoss()
        
        # Early stopping
        self.best_val_loss = float('inf')
        self.patience = config.get('patience', 10)
        self.patience_counter = 0
        
    def train_epoch(self):
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        all_predictions = []
        all_targets = []
        
        for batch_x, batch_y in self.train_loader:
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(batch_x).squeeze()
            # Patch: ensure shapes match for BCELoss
            outputs = outputs.view(-1)
            batch_y = batch_y.view(-1)
            loss = self.criterion(outputs, batch_y)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            
            # Store predictions for metrics
            predictions = (outputs > 0.5).float()
            all_predictions.extend(predictions.detach().numpy())
            all_targets.extend(batch_y.detach().numpy())
        
        # Calculate metrics
        avg_loss = total_loss / len(self.train_loader)
        f1 = f1_score(all_targets, all_predictions, zero_division=0)
        accuracy = accuracy_score(all_targets, all_predictions)
        
        return avg_loss, f1, accuracy
    
    def validate(self):
        """Validate the model."""
        self.model.eval()
        total_loss = 0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for batch_x, batch_y in self.val_loader:
                outputs = self.model(batch_x).squeeze()
                # Patch: ensure shapes match for BCELoss
                outputs = outputs.view(-1)
                batch_y = batch_y.view(-1)
                loss = self.criterion(outputs, batch_y)
                
                total_loss += loss.item()
                
                predictions = (outputs > 0.5).float()
                all_predictions.extend(predictions.numpy())
                all_targets.extend(batch_y.numpy())
        
        avg_loss = total_loss / len(self.val_loader)
        f1 = f1_score(all_targets, all_predictions, zero_division=0)
        accuracy = accuracy_score(all_targets, all_predictions)
        precision = precision_score(all_targets, all_predictions, zero_division=0)
        recall = recall_score(all_targets, all_predictions, zero_division=0)
        
        return avg_loss, f1, accuracy, precision, recall
    
    def train(self, epochs=100):
        """Full training loop with early stopping."""
        train_losses = []
        val_losses = []
        train_f1s = []
        val_f1s = []
        
        for epoch in range(epochs):
            # Training
            train_loss, train_f1, train_acc = self.train_epoch()
            
            # Validation
            val_loss, val_f1, val_acc, val_prec, val_rec = self.validate()
            
            # Store metrics
            train_losses.append(train_loss)
            val_losses.append(val_loss)
            train_f1s.append(train_f1)
            val_f1s.append(val_f1)
            
            # Log to MLflow
            mlflow.log_metrics({
                'train_loss': train_loss,
                'val_loss': val_loss,
                'train_f1': train_f1,
                'val_f1': val_f1,
                'train_accuracy': train_acc,
                'val_accuracy': val_acc,
                'val_precision': val_prec,
                'val_recall': val_rec
            }, step=epoch)
            
            # Early stopping
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                # Don't log model here - we'll log it once at the end
            else:
                self.patience_counter += 1
                
            if self.patience_counter >= self.patience:
                print(f"Early stopping at epoch {epoch}")
                break
                
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, Val F1: {val_f1:.4f}")
        
        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'train_f1s': train_f1s,
            'val_f1s': val_f1s,
            'best_val_f1': max(val_f1s)
        }

def create_sequences(features, targets, sequence_length=10):
    """
    Create sequences for time series data (same logic as existing implementation).
    """
    X, y = [], []
    for i in range(len(features) - sequence_length):
        X.append(features.iloc[i:i+sequence_length].values)
        y.append(targets.iloc[i+sequence_length])
    return np.array(X), np.array(y)

def prepare_data_for_training(data, sequence_length=10, test_size=0.2):
    """
    Prepare data for training with same preprocessing as existing implementation.
    """
    # Feature engineering (same as existing)
    features = []
    
    # Lagged features (1-5 lags)
    for lag in range(1, 6):
        features.append(data['spread'].shift(lag))
    
    # GARCH features (placeholder - will be replaced with actual GARCH)
    features.append(data['spread'].rolling(5).std())  # Placeholder for GARCH vol
    features.append(data['spread'].diff())  # Placeholder for GARCH resid
    
    # Technical indicators
    features.append(data['spread'].rolling(5).mean())  # MA_5
    features.append(data['spread'].rolling(20).mean())  # MA_20
    
    # RSI
    delta = data['spread'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    features.append(rsi)
    
    # Create feature matrix
    feature_df = pd.concat(features, axis=1)
    feature_df.columns = [f'lag_{i}' for i in range(1, 6)] + ['garch_vol', 'garch_resid', 'MA_5', 'MA_20', 'RSI']
    
    # Create target (same as existing)
    future_spread = data['spread'].shift(-1)
    current_spread = data['spread']
    target = ((future_spread - current_spread) * current_spread < 0).astype(int)
    
    # Drop NaN values
    feature_df = feature_df.dropna()
    target = target[feature_df.index]
    
    # Remove last row (where target is NaN)
    feature_df = feature_df.iloc[:-1]
    target = target.iloc[:-1]
    
    # Create sequences
    X, y = create_sequences(feature_df, target, sequence_length)
    
    # Split data
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    return X_train, X_test, y_train, y_test, feature_df.columns.tolist()

def train_gru_model_with_mlflow(data, config):
    """
    Train GRU model with MLflow integration.
    """
    # Import MLflow manager
    from src.mlflow_manager import get_mlflow_manager
    
    # Get MLflow manager
    mlflow_manager = get_mlflow_manager()
    
    # Create sector-specific experiment using the manager
    sector = config.get('sector', 'technology')
    experiment_name = f"pairs_trading/{sector}"
    mlflow_manager.set_experiment(experiment_name)
    
    # Create descriptive run name for long-running experiments
    pair_name = f"{config.get('pair_symbol1', 'unknown')}-{config.get('pair_symbol2', 'unknown')}"
    # For long-running experiments, use a stable run name with version
    # The timestamp is captured in MLflow's run metadata automatically
    run_name = f"GRU_Training_{pair_name}_v{config.get('version', '1')}"
    
    # Add descriptive tags
    tags = {
        "model_type": "GRU",
        "framework": "PyTorch",
        "implementation": "new_pytorch",
        "sector": "technology",
        "pair_symbols": pair_name,
        "version": f"v{config.get('version', '1')}",
        "run_type": "training",
        "experiment_type": "long_running"
    }
    
    with mlflow.start_run(run_name=run_name, tags=tags) as run:
        # Capture run info early
        run_id = run.info.run_id
        experiment_id = run.info.experiment_id
        
        # Log parameters
        mlflow.log_params(config)
        
        # Prepare data
        X_train, X_test, y_train, y_test, feature_names = prepare_data_for_training(
            data, 
            sequence_length=config['sequence_length']
        )
        
        # Log data info
        mlflow.log_params({
            'n_train_samples': len(X_train),
            'n_test_samples': len(X_test),
            'n_features': len(feature_names),
            'feature_names': feature_names
        })
        
        # Create datasets - use the 3D sequence data directly
        train_dataset = PairsDataset(
            X_train,  # Pass 3D numpy array directly
            y_train,  # Pass 1D numpy array directly
            sequence_length=config['sequence_length']
        )
        
        test_dataset = PairsDataset(
            X_test,  # Pass 3D numpy array directly
            y_test,  # Pass 1D numpy array directly
            sequence_length=config['sequence_length']
        )
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=config['batch_size'], shuffle=False)
        
        # Create model
        model = GRUPairsModel(
            input_size=len(feature_names),
            hidden_size=config['gru_units'],
            dropout=config['dropout_rate']
        )
        
        # Create trainer
        trainer = GRUTrainer(model, train_loader, test_loader, config)
        
        # Train model
        history = trainer.train(epochs=config['epochs'])
        
        # Log final metrics
        mlflow.log_metrics({
            'final_train_f1': history['train_f1s'][-1],
            'final_val_f1': history['val_f1s'][-1],
            'best_val_f1': history['best_val_f1']
        })
        
        # Log model with proper signature and metadata
        try:
            # Create a sample input for model signature (convert to numpy array)
            sample_input = torch.randn(1, config['sequence_length'], len(feature_names))
            sample_input_np = sample_input.detach().numpy()
            
            # Get naming pattern from config
            from src.utils.config_loader import load_config
            config_data = load_config()
            naming_pattern = config_data.get('model_registry', {}).get('naming_pattern', 'pairs_trading_gru_garch_{sector}_{version}')
            
            # Create model name using the pattern
            sector = config.get('sector', 'technology')
            version = config.get('version', 'v1')
            
            # For long-running experiments, use version-based naming
            # The timestamp is captured in the run metadata, not the model name
            model_name = naming_pattern.format(
                sector=sector,
                version=version
            )
            
            # Log model with signature
            mlflow.pytorch.log_model(
                model, 
                "model",
                input_example=sample_input_np,
                registered_model_name=model_name
            )
        except Exception as e:
            # Fallback to simple model logging if signature creation fails
            mlflow.pytorch.log_model(model, "model")
            print(f"Note: Model logged without signature due to: {e}")
        
        # Return run info along with model artifacts
        return model, history, trainer, run_id, experiment_id, run_name

if __name__ == "__main__":
    # Configuration (same as optimal from existing implementation)
    config = {
        'sequence_length': 10,
        'gru_units': 64,
        'dropout_rate': 0.255,
        'learning_rate': 0.0003,
        'batch_size': 32,
        'epochs': 100,
        'patience': 10
    }
    
    print("Starting PyTorch GRU migration with MLflow integration...")
    print(f"Configuration: {config}") 
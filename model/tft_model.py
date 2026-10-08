"""Basic TFT factory; no training, weights or manuscript predictions."""
from pytorch_forecasting.models import TemporalFusionTransformer
from pytorch_forecasting.metrics import MAE

def create_model(training, config):

    model_cfg = config["model"]

    # Loss
    loss = MAE() if model_cfg.get("loss", "MAE") == "MAE" else None

    model = TemporalFusionTransformer.from_dataset(
        training,
        learning_rate=model_cfg["learning_rate"],
        hidden_size=model_cfg["hidden_size"],
        attention_head_size=model_cfg["attention_head_size"],
        dropout=model_cfg["dropout"],
        hidden_continuous_size=model_cfg["hidden_continuous_size"],
        lstm_layers=model_cfg["lstm_layers"],
        loss=loss,
        log_interval=10,
        log_val_interval=1,
        reduce_on_plateau_patience=3,
    )

    print(model)
    return model

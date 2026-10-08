"""Inspect the basic factory and installed TFT source without instantiating a model."""
import argparse
import inspect
from importlib.metadata import version
from .tft_model import create_model, TemporalFusionTransformer

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--show-core', action='store_true', help='Print installed pytorch-forecasting TFT implementation')
    args = parser.parse_args()
    print('pytorch-forecasting:', version('pytorch-forecasting'))
    print('TFT class:', TemporalFusionTransformer.__module__ + '.' + TemporalFusionTransformer.__name__)
    print(inspect.getsource(create_model))
    if args.show_core:
        print(inspect.getsource(TemporalFusionTransformer))
    print('Inspection only. No model instantiated, no weights loaded, no predictions generated.')

if __name__ == '__main__':
    main()

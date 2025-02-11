import os
import sys
import yaml
import torch
import pprint
from munch import munchify
from models import VisModelingModel
from pytorch_lightning.strategies import DDPStrategy
# from pytorch_lightning.plugins import DDPPlugin
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint


def load_config(filepath):
    with open(filepath, 'r') as stream:
        try:
            trainer_params = yaml.safe_load(stream)
            return trainer_params
        except yaml.YAMLError as exc:
            print(exc)

def seed(cfg):
    torch.manual_seed(cfg.seed)
    if cfg.if_cuda:
        torch.cuda.manual_seed(cfg.seed)


def main():
    config_filepath = str(sys.argv[1])
    cfg = load_config(filepath=config_filepath)
    pprint.pprint(cfg)
    cfg = munchify(cfg)
    seed(cfg)
    seed_everything(cfg.seed)

    torch.set_float32_matmul_precision('medium')

    log_dir = '_'.join([cfg.log_dir,
                        cfg.model_name,
                        cfg.tag,
                        str(cfg.seed)])
    print(log_dir)

    model = VisModelingModel(lr=cfg.lr,
                             seed=cfg.seed,
                             dof=cfg.dof,
                             if_cuda=cfg.if_cuda,
                             if_test=False,
                             gamma=cfg.gamma,
                             log_dir=log_dir,
                             train_batch=cfg.train_batch,
                             val_batch=cfg.val_batch,
                             test_batch=cfg.test_batch,
                             num_workers=cfg.num_workers,
                             model_name=cfg.model_name,
                             data_filepath=cfg.data_filepath,
                             loss_type = cfg.loss_type,
                             coord_system=cfg.coord_system,
                             lr_schedule=cfg.lr_schedule)

    # define trainer
    trainer = Trainer(accelerator="gpu",
                     devices=cfg.num_gpus,
                     max_epochs=cfg.epochs,
                     deterministic=True,
                     strategy=DDPStrategy(find_unused_parameters=False),
                     precision="16-mixed",
                     default_root_dir=log_dir)

    trainer.fit(model)

def main_kinematic():
    config_filepath = str(sys.argv[1])
    cfg = load_config(filepath=config_filepath)
    pprint.pprint(cfg)
    cfg = munchify(cfg)
    seed(cfg)
    seed_everything(cfg.seed)

    log_dir = '_'.join([cfg.log_dir,
                        cfg.model_name,
                        cfg.tag,
                        str(cfg.seed)])

    model = VisModelingModel(lr=cfg.lr,
                             seed=cfg.seed,
                             dof=cfg.dof,
                             if_cuda=cfg.if_cuda,
                             if_test=False,
                             gamma=cfg.gamma,
                             log_dir=log_dir,
                             train_batch=cfg.train_batch,
                             val_batch=cfg.val_batch,
                             test_batch=cfg.test_batch,
                             num_workers=cfg.num_workers,
                             model_name=cfg.model_name,
                             data_filepath=cfg.data_filepath,
                             loss_type = cfg.loss_type,
                             coord_system=cfg.coord_system,
                             lr_schedule=cfg.lr_schedule)

    # define callback for selecting checkpoints during training
    checkpoint_callback = ModelCheckpoint(
        filename=log_dir + "{epoch}_{val_loss}",
        verbose=True,
        monitor='val_loss',
        mode='min',
        prefix='')
    
    # define trainer
    trainer = Trainer(accelerator="gpu",
                     devices=cfg.num_gpus,
                     max_epochs=cfg.epochs,
                     deterministic=True,
                     strategy=DDPStrategy(find_unused_parameters=False),
                     precision="16-mixed",
                     default_root_dir=log_dir,
                     val_check_interval=1.0,
                     callbacks=[checkpoint_callback])

    model.extract_kinematic_encoder_model(sys.argv[3])
    trainer.fit(model)

def main_kinematic_scratch():
    config_filepath = str(sys.argv[1])
    cfg = load_config(filepath=config_filepath)
    pprint.pprint(cfg)
    cfg = munchify(cfg)
    seed(cfg)
    seed_everything(cfg.seed)

    torch.set_float32_matmul_precision('medium')

    log_dir = '_'.join([cfg.log_dir,
                        cfg.model_name,
                        cfg.tag,
                        str(cfg.seed)])

    model = VisModelingModel(lr=cfg.lr,
                             seed=cfg.seed,
                             dof=cfg.dof,
                             if_cuda=cfg.if_cuda,
                             if_test=False,
                             gamma=cfg.gamma,
                             log_dir=log_dir,
                             train_batch=cfg.train_batch,
                             val_batch=cfg.val_batch,
                             test_batch=cfg.test_batch,
                             num_workers=cfg.num_workers,
                             model_name=cfg.model_name,
                             data_filepath=cfg.data_filepath,
                             loss_type = cfg.loss_type,
                             coord_system=cfg.coord_system,
                             lr_schedule=cfg.lr_schedule)

    # define callback for selecting checkpoints during training
    checkpoint_callback = ModelCheckpoint(
        filename=log_dir + "{epoch}_{val_loss}",
        verbose=True,
        monitor='val_loss',
        mode='min',
        prefix='')
    
    # define trainer
    trainer = Trainer(accelerator="gpu",
                     devices=cfg.num_gpus,
                     max_epochs=cfg.epochs,
                     deterministic=True,
                     strategy=DDPStrategy(find_unused_parameters=False),
                     precision="16-mixed",
                     default_root_dir=log_dir,
                     val_check_interval=1.0,
                     callbacks=[checkpoint_callback])
                      
    trainer.fit(model)


if __name__ == '__main__':
    if sys.argv[2] == 'kinematic':
        main_kinematic()
    elif sys.argv[2] == 'kinematic-scratch':
        main_kinematic_scratch()
    else:
        main()

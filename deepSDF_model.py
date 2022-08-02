# author: Sylvain Laporte
# program: deepSDF_model.py
# date: 2020-12-08
# object: DeepSDF model definition in PyTorch for local use.

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import weight_norm

loss_function = nn.L1Loss()

def accuracy(outputs, sdf_values):
    """For human validation only"""
    pass

class DeepSDF_single(nn.Module):
    """Multi-layer fully-connected feed-forward neural network with 8 layers, each applied with dropout"""
    def __init__(self, in_size, hidden_size, out_size):
        super().__init__()
        # Hidden layer 1
        self.linear1 = weight_norm(nn.Linear(in_size, hidden_size))
        # Hidden layer 2
        self.linear2 = weight_norm(nn.Linear(hidden_size, hidden_size))
        # Hidden layer 3
        self.linear3 = weight_norm(nn.Linear(hidden_size, hidden_size))
        # Hidden layer 4
        self.linear4 = weight_norm(nn.Linear(hidden_size, hidden_size))
        # Hidden layer 5
        self.linear5 = weight_norm(nn.Linear(hidden_size, hidden_size))
        # Hidden layer 6
        self.linear6 = weight_norm(nn.Linear(hidden_size, hidden_size))
        # Hidden layer 7
        self.linear7 = weight_norm(nn.Linear(hidden_size, hidden_size))
        # Output layer
        self.linear8 = weight_norm(nn.Linear(hidden_size, out_size))

    def forward(self, xb):
        out = self.linear1(xb)
        out = F.dropout(out)
        out = F.relu(out)
        out = self.linear2(out)
        out = F.dropout(out)
        out = F.relu(out)
        out = self.linear3(out)
        out = F.dropout(out)
        out = F.relu(out)
        out = self.linear4(out)
        out = F.dropout(out)
        out = F.relu(out)
        out = self.linear5(out)
        out = F.dropout(out)
        out = F.relu(out)
        out = self.linear6(out)
        out = F.dropout(out)
        out = F.relu(out)
        out = self.linear7(out)
        out = F.dropout(out)
        out = F.relu(out)
        out = self.linear8(out)
        out = F.dropout(out)
        out = F.tanh(out)
        return out
    
    def training_step(self, batch):
        point_samples, sdf_values = batch
        out = self(point_samples)               # generate predictions
        loss = loss_function(out, sdf_values)   # compute loss
        return loss

    def validation_step(self, batch):
        point_samples, sdf_values = batch
        out = self(point_samples)               # generate predictions
        loss = loss_function(out, sdf_values)   # compute loss
        acc = accuracy(out, sdf_values)         # compute accuracy
        return {'val_loss': loss, 'val_acc': acc}
    
    def validation_epoch_end(self, outputs):
        batch_losses = [x['val_loss'] for x in outputs]
        epoch_loss = torch.stack(batch_losses).mean()   # combine losses
        return {'val_loss': epoch_loss.item()}

        # batch_accs = [x['val_acc'] for x in outputs]
        # epoch_acc = torch.stack(batch_accs).mean()      # combine accuracies
        # return {'val_loss': epoch_loss.item(), 'val_acc': epoch_acc.item()}
    
    def epoch_end(self, epoch, result):
        print("Epoch [{}], val_loss: {:.4f}".format(epoch, result['val_loss'],))
        # print("Epoch [{}], val_loss: {:.4f}, val_acc: {:.4f}".format(epoch, result['val_loss'], result['val_acc']))
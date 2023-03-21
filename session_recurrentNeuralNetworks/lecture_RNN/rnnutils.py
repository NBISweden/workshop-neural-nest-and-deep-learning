import os
import sys
import math
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense, SimpleRNN, LSTM, GRU
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
import matplotlib

font = {
    'size'   : 12
}
matplotlib.rc('font', **font)


def make_train_test(data, train_fraction=0.67, rescale=True):
    """Create train and test data set from a data vector.

    Args:
      data (np.array): data array
      train_fraction (float): fraction of data devoted to training

    Returns:
      (train, test, data): 3-tuple of train, test, and original data
    """
    split = int(len(data) * train_fraction)
    if rescale:
        scaler = MinMaxScaler(feature_range=(0, 1))
    else:
        scaler = MinMaxScaler(feature_range=(min(data), max(data)))
    data = scaler.fit_transform(data).flatten()
    train = data[range(split)]
    test = data[split:]
    return train, test, scaler


def make_xy(data, window_size=1, step_size=1):
    """Create X, Y data pairs from a dataset vector.

    Args:
      data (float, int): dataset vector
      window_size (int): window size; number of dataset points looking back
      step_size (int): step size between windows

    Returns:
      (X, Y): X, Y data pair
    """
    X_indices = []
    X = []
    Y_indices = np.arange(window_size, len(data), step_size)
    Y = data[Y_indices]
    j = 0
    for i, _ in enumerate(Y_indices):
        ind = list(range(j, j + window_size))
        j = j + step_size
        X_indices.append(ind)
        X.append(data[ind])
    X = np.reshape(np.array(X), (len(Y), window_size, 1))
    return X, Y, np.array(X_indices), Y_indices


def plot_pred(data, scaler=None, rmse=True, plotmarkers=False, **kw):
    """Plot prediction and original data"""
    ticks = kw.pop("ticks", None)
    labels = kw.pop("labels", None)
    fig, ax = plt.subplots(**kw)
    legend = []
    rmsedata = {}
    markers = ["*", "x", "o"]
    colors = ["black", "steelblue", "darkred", "green"]
    x = []
    y = []
    shift = 0
    for k, v in data.items():
        if v is None:
            continue
        Ypred, Y, Y_indices = v
        X = np.arange(len(Y)) + shift
        shift = shift + len(X)
        if scaler is not None:
            Y = scaler.inverse_transform(Y.reshape(-1, 1)).flatten()
            Ypred = scaler.inverse_transform(Ypred.reshape(-1, 1)).flatten()
        e = math.sqrt(mean_squared_error(Y[Y_indices], Ypred))
        if rmse:
            k = f"{k} (RMSE: {e:.4f})"
        legend.append(k)
        col = colors.pop()
        ax.plot(X[Y_indices], Ypred, color=col)
        if plotmarkers:
            ax.plot(X[Y_indices], Ypred, markers.pop(), color=col)
        x.extend(X)
        y.extend(Y)
    legend.append("Data")
    ax.plot(x, y, '-', color=colors.pop())
    ax.set_title("Model prediction")
    if ticks is not None and labels is not None:
        ax.set_xticks(ticks, labels=labels)
    ax.legend(legend)
    plt.show()


def plot_loss_acc(history):
    try:
        plt.plot(history.history['accuracy'])
        plt.plot(history.history['val_accuracy'])
    except:
        plt.plot(history.history['acc'])
        plt.plot(history.history['val_acc'])

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train acc', 'val acc', 'train loss', 'val loss'], loc='upper left')
    plt.show()

def plot_history(history, show=True, xlim=None, ylim=None, **kw):
    """Plot history - plot training and/or test accuracy or loss values"""
    datalabels = ["Training", "Validation"]
    metrics_labels = {'loss': "loss", 'acc': "accuracy", 'accuracy': "accuracy",
                      'mse': 'mse', 'recall': 'recall'}
    if not isinstance(history, dict):
        history = history.history
    hkeys = history.keys()
    h = np.array([history[k] for k in hkeys])
    labels = ["{} {}".format(x, y) for x, y in zip([datalabels[u.startswith("val_")] for u in hkeys],
                                                   [metrics_labels[v.replace("val_", "")] for v in hkeys])]
    fig, ax = plt.subplots(**kw)
    ax.plot(np.array(range(0, h.shape[1])), h.T)
    ax.set_title('Model metrics')
    ax.set_ylabel('Metric')
    ax.set_xlabel('Epoch')
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.legend([l for l in labels], loc='upper left')
    if show:
        plt.show()


def airlines():
    """Load and reformat airlines data set"""
    fn = "airline-passengers.csv"
    if not os.path.exists(fn):
        print(f"Download airline passenger data: 'wget https://raw.githubusercontent.com/jbrownlee/Datasets/master/{fn} --no-check-certificate'")
        sys.exit(1)
    df = pd.read_csv(fn)
    df = df.rename(columns={'Month': 'time','Passengers': 'passengers'})
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m')
    df['year'] = pd.DatetimeIndex(df['time']).year
    df['month'] = pd.DatetimeIndex(df['time']).month
    return df

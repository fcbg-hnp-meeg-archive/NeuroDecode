"""
Regularized LDA

The code was implemented based on the following paper:
Dornhege et al., "General Signal Processing and Machine Learning Tools for
BCI Analysis Toward Brain-Computer Interfacing", MIT Press, 2007, page 218.

Kyuhwa Lee
Swiss Federal Institute of Technology Lausanne (EPFL)
"""

import math
import numpy as np


class rLDA:
    def __init__(self, reg_cov=None):
        if reg_cov > 1:
            raise RuntimeError('reg_cov > 1')
        self.lambdaStar = reg_cov

    def fit(self, X, Y):
        """
        Train rLDA

        Parameters
        ----------
        X : np.ndarray (samples, features)
            2D. Data to use for training.
        Y : np.ndarray
            1D. Labels to use for training. 2 labels must be present in Y.

        Returns
        -------
        np.ndarray (samples, )
            The weight vector.
        b : bias scalar.

        Note that the rLDA object itself is also updated with w and b, i.e.,
        the return values can be safely ignored.
        """
        if type(X) is list:
            X = np.array(X)
        if type(Y) is list:
            Y = np.array(Y)

        labels = np.unique(Y)
        if X.ndim != 2:
            raise RuntimeError('X must be 2 dimensional.')
        if len(labels) != 2 or labels[0] == labels[1]:
            raise RuntimeError('Exactly two different labels required.')

        index1 = np.where(Y == labels[0])[0]
        index2 = np.where(Y == labels[1])[0]
        cov = np.matrix(np.cov(X.T))
        mu1 = np.matrix(np.mean(X[index1], axis=0).T).T
        mu2 = np.matrix(np.mean(X[index2], axis=0).T).T
        mu = (mu1 + mu2) / 2
        numFeatures = X.shape[1]

        if self.lambdaStar is not None and numFeatures > 1:
            cov = (1 - self.lambdaStar) * cov + (self.lambdaStar /
                                                 numFeatures) * np.trace(cov) * np.eye(cov.shape[0])

        w = np.linalg.pinv(cov) * (mu2 - mu1)
        b = -(w.T) * mu

        for wi in w:
            assert not math.isnan(wi)
        assert not math.isnan(b)

        self.coef_ = np.array(w)  # vector
        self.b = np.array(b)  # scalar
        self.classes_ = labels

        return self.coef_, self.b

    def predict(self, X, proba=False):
        """
        Returns the predicted class labels optionally with likelihoods.
        """
        probs = []
        predicted = []
        for row in X:
            probability = float(self.coef_.T * np.matrix(row).T + self.b.T)
            if probability >= 0:
                predicted.append(self.classes_[1])
            else:
                predicted.append(self.classes_[0])

            # rescale from 0 to 1, similar to scikit-learn's way
            prob_norm = 1.0 / (np.exp(-probability / 10.0) + 1.0)
            # values are in the same order as that of self.classes_
            probs.append([1 - prob_norm, prob_norm])

        if proba:
            return np.array(probs)
        else:
            return predicted

    def predict_proba(self, X):
        """
        Returns the predicted class labels and likelihoods.
        """
        return self.predict(X, proba=True)

    def get_labels(self):
        """
        Returns labels in the same order as you get when you call predict().
        """
        return self.classes_

    def score(self, X, true_labels):
        raise NotImplementedError(
            'Sorry. this function is not implemented yet.')

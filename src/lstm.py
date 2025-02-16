import torch
import torch.nn as nn
import numpy as np


class LSTM(nn.Module):
    def __init__(self, embedding_matrix: np.ndarray):
        """
        :param embedding_matrix: numpy array with vectors for all words
        """
        super(LSTM, self).__init__()
        # number of words = number of rows in embedding matrix
        num_words = embedding_matrix.shape[0]
        # dimension of embedding is num of columns in the matrix
        embed_dim = embedding_matrix.shape[1]

        # we define an input embedding layer
        self.embedding = nn.Embedding(num_embeddings=num_words, embedding_dim=embed_dim)

        # embedding matrix is used as weights of the embedding layer
        self.embedding.weight = nn.Parameter(
            torch.tensor(embedding_matrix, dtype=torch.float32)
        )

        # we don't want to train the pre-trained embeddings
        self.embedding.weight.requires_grad = False

        # a simple bidirectional LSTM with hidden size of 128
        self.lstm = nn.LSTM(
            embed_dim,
            128,
            bidirectional=True,
            batch_first=True,
        )

        # output layer which is a linear layer, we have only one output
        # input (512) = 128 + 128 for mean and same for max pooling
        self.out = nn.Linear(512, 1)

    def forward(self, x):
        # input is 16 (batch size) * 128 (max sequence length)

        # pass data through embedding layer
        # the input is just the tokens
        x = self.embedding(x)

        # 16 x 128 x 300

        # move embedding output to lstm

        # 16 x 128 x 256 
        x, _ = self.lstm(x)  

        # apply mean and max pooling on lstm output
        avg_pool = torch.mean(x, 1) # 16 x 256
        max_pool, _ = torch.max(x, 1) # 16 x 256 

        # concatenate mean and max pooling
        # this is why size is 512
        # 128 for each direction = 256
        # avg_pool = 256 and max_pool = 256
        out = torch.cat((avg_pool, max_pool), 1) # 16 * 512

        # pass through the output layer and return the output
        out = self.out(out)

        # return linear output
        return out

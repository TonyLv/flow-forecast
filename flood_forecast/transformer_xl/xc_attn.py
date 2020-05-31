import torch
class TransformerModel(torch.nn.Module):
    """ Transformer model """
    def __init__(self,args,input_dim, n_head, seq_num, layer, n_embd, win_len, device):
        super(TransformerModel, self).__init__()
        self.input_dim = input_dim
        self.n_head = n_head
        self.seq_num = seq_num
        self.n_embd = n_embd
        self.win_len = win_len
        self.dataset = args.dataset
        self.id_embed = torch.nn.Embedding(seq_num,n_embd)
        self.po_embed = torch.nn.Embedding(win_len,n_embd)
        self.drop_em = torch.nn.Dropout(args.embd_pdrop)
        self.device = device
        self.xc_encoder = TransformerEncoderLayer()
        torch.nn.init.normal_(self.id_embed.weight, std=0.02)
        torch.nn.init.normal_(self.po_embed.weight, std=0.02)

    def forward(self,series_id, x):
        id_embedding = self.id_embed(series_id)
        length = x.size(1) # (Batch_size,length,input_dim)
        position = torch.tensor(torch.arange(length),dtype=torch.long).to(self.device)
        po_embedding = self.po_embed(position)
        batch_size = x.size(0)
        embedding_sum = torch.zeros(batch_size,length,self.n_embd).to(self.device)
        embedding_sum[:] = po_embedding
        embedding_sum = embedding_sum + id_embedding.unsqueeze(1)
        x = torch.cat((x,embedding_sum),dim=2)
        
        return x

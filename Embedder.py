#Class for creating the embedding of the documents
from transformers import AutoTokenizer, AutoModelForMaskedLM, RobertaTokenizer, RobertaModel
from utils import preprocessing
import numpy as np
import math
import torch
class Embedder:
    def __init__(self, model_name : str='roberta-base', max_length : int = 512):
        if model_name == 'roberta-base':
            self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
            self.model = RobertaModel.from_pretrained(model_name, output_hidden_states=True)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForMaskedLM.from_pretrained(model_name)
        self.max_length = max_length -2 # start endtoken
    def embed(self, text : str) -> np.array:
        """
        Embed a given text into a vector
        :param text: the text to embed already preprocessed
        :return: the embedding of the text
        """
        # splitting the text into sentences
        encoded_input = self.tokenizer.tokenize(text) # tokenized text into subwords
        token_count = len(encoded_input)
        if token_count > self.max_length: # now token must be splitted up
            split = math.ceil(token_count/self.max_length)
            inputs = []
            masks = []
            for i in range(split):
                chunk = encoded_input[i*self.max_length:(i+1)*self.max_length]
                tokenized_input = self.tokenizer.encode_plus(chunk, add_special_tokens=True, return_tensors='pt', padding= 'max_length')
                inputs.append(tokenized_input['input_ids'])
                masks.append(tokenized_input['attention_mask'])
            bt_inputs = torch.stack(inputs, dim=0).squeeze()
            bt_masks = torch.stack(masks, dim=0).squeeze()
        else:
            tokenized_input = self.tokenizer.encode_plus(encoded_input, add_special_tokens=True, return_tensors='pt')
            bt_inputs = tokenized_input['input_ids']
            bt_masks = tokenized_input['attention_mask']
        with torch.no_grad():
            output = self.model(input_ids=bt_inputs, attention_mask=bt_masks)
            token_embeddings = output.hidden_states[-2] #take the second to last
            total_embedding = torch.mean(token_embeddings, dim=(0,1)).detach().numpy()
        return total_embedding

if __name__ == '__main__':
    embedder = Embedder('roberta-base')
    text = 'I love to eat apples'
    text = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas dignissim velit et velit convallis, eget consequat lacus efficitur. Nulla facilisi. In hac habitasse platea dictumst. Integer faucibus risus sed lobortis ullamcorper. Fusce rhoncus efficitur rutrum. Nullam rutrum bibendum velit, sed gravida massa ullamcorper ac. Quisque at ligula ultricies, faucibus est vel, placerat arcu. Vestibulum tincidunt finibus elit, a convallis felis dapibus vel. Donec convallis dolor vel turpis aliquam pulvinar. Ut posuere elit vitae venenatis tincidunt. In non orci at metus facilisis viverra. Nunc lacinia erat nec iaculis tristique. Phasellus ac pulvinar lorem. Nam faucibus quam a mi facilisis tempus.

    Sed vitae aliquet arcu, at hendrerit tortor. Pellentesque sit amet ligula vel tellus laoreet dignissim et a urna. Mauris et lacinia lectus. Ut vitae purus eget nisl aliquet rhoncus. Sed aliquam sapien sed tincidunt sollicitudin. Mauris lobortis ex vel laoreet pharetra. Mauris eget nunc sit amet leo finibus pellentesque nec vel nisi. Aliquam erat volutpat. Cras ac augue ut turpis gravida faucibus a et ex. In hac habitasse platea dictumst. Sed commodo diam in dictum finibus. Morbi tristique tellus justo, at interdum velit facilisis nec. Curabitur ut nisl non nulla tempus laoreet. Nunc consequat, risus id aliquet pharetra, lectus massa consectetur dolor, sit amet consectetur ligula massa eget quam.

    Praesent ac scelerisque purus. Vivamus eu nisl eget neque pharetra cursus eget sit amet odio. Fusce a mi malesuada, posuere neque ac, ullamcorper sem. Nulla bibendum dolor id turpis sollicitudin, ut feugiat ipsum rhoncus. Mauris quis leo vitae mauris facilisis congue. In hac habitasse platea dictumst. Donec ut congue quam, eget ullamcorper odio. Proin non leo auctor, fringilla dolor vel, bibendum risus. Sed ut tellus at neque pharetra iaculis et ac arcu. Aliquam mattis, justo ac fermentum sollicitudin, velit est luctus tortor, ut lobortis ante purus sed nulla.

    Etiam condimentum lorem non sapien egestas, eu finibus purus efficitur. Vivamus et est sed ipsum consequat pharetra. Morbi dignissim nisi quis dolor vulputate, eu facilisis nulla condimentum. Pellentesque ullamcorper elementum quam, ut tincidunt lectus hendrerit non. Nam interdum, velit sed ullamcorper facilisis, purus arcu aliquet turpis, vitae convallis tortor quam vel elit. Nulla facilisi. Nulla suscipit aliquam lectus, ut faucibus tortor rhoncus eu. Donec a nisl facilisis, egestas orci sed, dignissim mauris. Suspendisse potenti. Proin dictum varius elit, ut gravida enim tempor id. Nulla vitae faucibus leo. Vestibulum ullamcorper mauris dolor, vitae lacinia sem malesuada nec. Nam ut enim sit amet lacus fermentum fringilla. Proin id urna consequat, tempus lacus ac, commodo est. Sed dapibus orci in elit pellentesque, sed ullamcorper ante finibus. Aliquam blandit purus id lectus blandit, id hendrerit turpis elementum. Curabitur volutpat tortor quis augue ultricies, a facilisis justo elementum.

    Duis non urna sit amet purus bibendum maximus. Nullam congue, ligula a tincidunt viverra, nisl turpis efficitur velit, in rhoncus dui nunc sed neque. Suspendisse tempor, elit et tincidunt faucibus, diam mi lacinia metus, sed elementum metus tortor id erat. Curabitur suscipit feugiat metus non blandit. Mauris vulputate quam ac fermentum venenatis. Sed elementum urna eu venenatis pharetra. Nulla efficitur massa ac justo dictum dignissim.

    Praesent ac scelerisque purus. Vivamus eu nisl eget neque pharetra cursus eget sit amet odio. Fusce a mi malesuada, posuere neque ac, ullamcorper sem. Nulla bibendum dolor id turpis sollicitudin, ut feugiat ipsum rhoncus. Mauris quis leo vitae mauris facilisis congue. In hac habitasse platea dictumst. Donec ut congue quam, eget ullamcorper odio. Proin non leo auctor, fringilla dolor vel, bibendum risus. Sed ut tellus at neque pharetra iaculis et ac arcu. Aliquam mattis, justo ac fermentum sollicitudin, velit est luctus tortor, ut lobortis ante purus sed nulla.

    Etiam condimentum lorem non sapien egestas, eu finibus purus efficitur. Vivamus et est sed ipsum consequat pharetra. Morbi dignissim nisi quis dolor vulputate, eu facilisis nulla condimentum. Pellentesque ullamcorper elementum quam, ut tincidunt lectus hendrerit non. Nam interdum, velit sed ullamcorper facilisis, purus arcu aliquet turpis, vitae convallis tortor quam vel elit. Nulla facilisi. Nulla suscipit aliquam lectus, ut faucibus tortor rhoncus eu. Donec a nisl facilisis, egestas orci sed, dignissim mauris. Suspendisse potenti. Proin dictum varius elit, ut gravida enim tempor id. Nulla vitae faucibus leo. Vestibulum ullamcorper mauris dolor, vitae lacinia sem malesuada nec. Nam ut enim sit amet lacus fermentum fringilla. Proin id urna consequat, tempus lacus ac, commodo est. Sed dapibus orci in elit pellentesque, sed ullamcorper ante finibus. Aliquam blandit purus id lectus blandit, id hendrerit turpis elementum. Curabitur volutpat tortor quis augue ultricies, a facilisis justo elementum.

    Praesent ac scelerisque purus. Vivamus eu nisl eget neque pharetra cursus eget sit amet odio. Fusce a mi malesuada, posuere neque ac, ullamcorper sem. Nulla bibendum dolor id turpis sollicitudin, ut feugiat ipsum rhoncus. Mauris quis leo vitae mauris facilisis congue. In hac habitasse platea dictumst. Donec ut congue quam, eget ullamcorper odio. Proin non leo auctor, fringilla dolor vel, bibendum risus. Sed ut tellus at neque pharetra iaculis et ac arcu. Aliquam mattis, justo ac fermentum sollicitudin, velit est luctus tortor, ut lobortis ante purus sed nulla.

    Etiam condimentum lorem non sapien egestas, eu finibus purus efficitur. Vivamus et est sed ipsum consequat pharetra. Morbi dignissim nisi quis dolor vulputate, eu facilisis nulla condimentum. Pellentesque ullamcorper elementum quam, ut tincidunt lectus hendrerit non. Nam interdum, velit sed ullamcorper facilisis, purus arcu aliquet turpis, vitae convallis tortor quam vel elit. Nulla facilisi. Nulla suscipit aliquam lectus, ut faucibus tortor rhoncus eu. Donec a nisl facilisis, egestas orci sed, dignissim mauris. Suspendisse potenti. Proin dictum varius elit, ut gravida enim tempor id. Nulla vitae faucibus leo. Vestibulum ullamcorper mauris dolor, vitae lacinia sem malesuada nec. Nam ut enim sit amet lacus fermentum fringilla. Proin id urna consequat, tempus lacus ac, commodo est. Sed dapibus orci in elit pellentesque, sed ullamcorper ante finibus. Aliquam blandit purus id lectus blandit, id hendrerit turpis elementum. Curabitur volutpat tortor quis augue ultricies, a facilisis justo elementum.

    ... (repeated text) ...

    Etiam porttitor, lacus ut suscipit scelerisque, mauris felis iaculis velit, nec ultricies tortor urna ut enim. Nam varius vulputate velit ac volutpat. Nunc finibus enim felis, sit amet ullamcorper justo pharetra id. Nam vehicula metus sit amet tortor luctus viverra. Morbi ac felis non lacus egestas posuere. Proin blandit finibus nunc, eu condimentum dui pulvinar eu. Aenean ultrices nulla vitae eros tristique scelerisque. Fusce a est vel mi fermentum blandit. Vivamus tincidunt ultricies bibendum. Nunc pulvinar purus eget lacus aliquam, eget ullamcorper est dictum. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Sed in finibus dolor. Sed id scelerisque purus, eu semper ligula. Aliquam gravida ullamcorper purus, nec sollicitudin neque dictum non.
    '''
    text = preprocessing(text)

    embedding = embedder.embed(text)
    print(embedding.shape)
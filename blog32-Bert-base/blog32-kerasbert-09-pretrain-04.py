# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 00:09:48 2021
@author: xiuzhang
"""
import os
from keras_bert import load_vocabulary
from keras_bert import Tokenizer
from keras_bert import load_trained_model_from_checkpoint
import numpy as np

#-------------------------------第一步 加载模型--------------------------------- 
#设置预训练模型的路径
pretrained_path = 'chinese_L-12_H-768_A-12'
config_path = os.path.join(pretrained_path, 'bert_config.json')
checkpoint_path = os.path.join(pretrained_path, 'bert_model.ckpt')
vocab_path = os.path.join(pretrained_path, 'vocab.txt')
 
#构建字典
token_dict = load_vocabulary(vocab_path)
print(token_dict)
print(len(token_dict))

#Tokenization
tokenizer = Tokenizer(token_dict)
print(tokenizer)

#加载预训练模型
model = load_trained_model_from_checkpoint(config_path, checkpoint_path)
print(model)

#-------------------------------第二步 特征提取--------------------------------- 
text = '语言模型'
tokens = tokenizer.tokenize(text)
print(tokens)
#['[CLS]', '语', '言', '模', '型', '[SEP]']

indices, segments = tokenizer.encode(first=text, max_len=512)
print(indices[:10])
print(segments[:10])
 
#提取特征
predicts = model.predict([np.array([indices]), np.array([segments])])[0]
for i, token in enumerate(tokens):
    print(token, predicts[i].tolist()[:5])
print("")

#----------------------------第三步 多句子特征提取------------------------------
text1 = '语言模型'
text2 = "你好"
tokens1 = tokenizer.tokenize(text1)
print(tokens1)
tokens2 = tokenizer.tokenize(text2)
print(tokens2)
 
indices_new, segments_new = tokenizer.encode(first=text1, second=text2 ,max_len=512)
print(indices_new[:10])
#[101, 6427, 6241, 3563, 1798, 102, 0, 0, 0, 0]
print(segments_new[:10])
#[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
 
#提取特征
predicts_new = model.predict([np.array([indices_new]), np.array([segments_new])])[0]
for i, token in enumerate(tokens1):
    print(token, predicts_new[i].tolist()[:5])
for i, token in enumerate(tokens2):
    print(token, predicts_new[i].tolist()[:5])

#------------------------------第四步 字词预测填充------------------------------
#加载语言模型
model = load_trained_model_from_checkpoint(config_path, checkpoint_path, training=True)
token_dict_rev = {v: k for k, v in token_dict.items()}
token_ids, segment_ids = tokenizer.encode(
    u'数学是利用符号语言研究数量、结构、变化以及空间等概念的一门学科', 
    max_len=512)

#mask掉“数学”
print(token_ids[1],token_ids[2])
token_ids[1] = token_ids[2] = tokenizer._token_dict['[MASK]']
masks = np.array([[0, 1, 1] + [0] * (512 - 3)])
 
#模型预测被mask掉的部分
probas = model.predict([np.array([token_ids]), np.array([segment_ids]), masks])[0]
pred_indice = probas[0][1:3].argmax(axis=1).tolist()
print('Fill with: ', list(map(lambda x: token_dict_rev[x], pred_indice)))
#Fill with:  ['数', '学']

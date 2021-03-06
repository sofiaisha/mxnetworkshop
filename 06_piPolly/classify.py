import mxnet as mx
import numpy as np
import cv2,sys,time
from collections import namedtuple
import camera,polly

def loadModel(modelname):
	sym, arg_params, aux_params = mx.model.load_checkpoint(modelname, 0)
	arg_params['prob_label'] = mx.nd.array([0])
	mod = mx.mod.Module(symbol=sym)
	mod.bind(for_training=False, data_shapes=[('data', (1,3,224,224))])
	mod.set_params(arg_params, aux_params)
	return mod

def loadCategories():
	synsetfile = open('synset.txt', 'r')
	synsets = []
	for l in synsetfile:
		synsets.append(l.rstrip())
	return synsets

def prepareNDArray(filename):
	img = cv2.imread(filename)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	img = cv2.resize(img, (224, 224,))
	img = np.swapaxes(img, 0, 2)
    	img = np.swapaxes(img, 1, 2)
    	img = img[np.newaxis, :]
	return mx.nd.array(img) 

def predict(filename, model, categories, n):
	array = prepareNDArray(filename)
	Batch = namedtuple('Batch', ['data'])
	t1 = time.time()
	model.forward(Batch([array]))
    	prob = model.get_outputs()[0].asnumpy()
	t2 = time.time()
	print (t2-t1)

	prob = np.squeeze(prob)
    	sortedprobindex = np.argsort(prob)[::-1]
	topn = []
    	for i in sortedprobindex[0:n]:
        	topn.append((prob[i], categories[i]))
    	return topn

def init(modelname): 
	model = loadModel(modelname)
	cats = loadCategories()
	return model, cats

def build_top1_message(topN):
    top1 = topN[0]
    # Convert probability to integer percentage
    prob = (str)((int)(top1[0]*100))
    # Remove category number
    item = top1[1].split(' ')
    item = ' '.join(item[1:])
    message = "I'm "+prob+"% sure that this is a "+item+". "
    return message

if __name__ == "__main__":

	filename = "myimage.jpg"
	# camera.takePicture(filename)

	inceptionv3,c = init("Inception-BN")
	top5 = predict(filename,inceptionv3,c,5)
	print top5

	message = build_top1_message(top5)
	print message

	#
	# TO DO: use Polly to speak the message (see polly.py)
	#


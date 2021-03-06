# -------------------------------------------
# Training FCN for image segmentation
# -------------------------------------------
import argparse
import os
import time
from keras.preprocessing import image
import numpy as np
from PIL import Image
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
import keras

import fcn

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--weights", help="weightfile", type=str)
args = parser.parse_args()

# if weights argument is provided, start training from initial state
if args.weights:
    fcn.model.load_weights(args.weights)

cwd = os.path.dirname(__file__)

# load masks from disk
masks_path = 'data/train_segmentation/masks'
masks = os.listdir(masks_path)

imgs = []
for imgPath in masks:
  img = image.load_img(os.path.join(masks_path, imgPath), target_size=(fcn.img_width, fcn.img_height), grayscale = True)
  x = np.asarray(img).reshape((256, 256, 1))
  x = np.expand_dims(x, axis=0)
  x = x * (1./255)
  x[x > 0.5] = 1
  x[x <= 0.5] = 0
  imgs.append(x)

npimgs = np.vstack(imgs) #masks

# load tiles from disk
tiles_path = 'data/train_segmentation/tiles'
tiles = os.listdir(tiles_path)

timgs = []
for imgPath in tiles:
  img = image.load_img(os.path.join(tiles_path, imgPath), target_size=(fcn.img_width, fcn.img_height))
  x = np.asarray(img)
  x = np.expand_dims(x, axis=0)
  x = x * (1./255)
  timgs.append(x)

nptileimgs = np.vstack(timgs) #tiles

# image augmentation data generator setup
data_gen_args = dict(
  fill_mode='reflect',
  shear_range=0.1,
  rotation_range=90.,
  width_shift_range=0.1,
  height_shift_range=0.1,
  zoom_range=0.2
)
image_datagen = image.ImageDataGenerator(**data_gen_args)
mask_datagen = image.ImageDataGenerator(**data_gen_args)
seed = 1
image_datagen.fit(nptileimgs[:10], augment=True, seed=seed)
mask_datagen.fit(npimgs[:10], augment=True, seed=seed)

image_generator = image_datagen.flow(nptileimgs, seed=seed, batch_size=10000)
mask_generator = mask_datagen.flow(npimgs, seed=seed, batch_size=10000)

# simple logger to show acc and loss even when running as a service
class LossHistory(keras.callbacks.Callback):
  def on_batch_end(self, batch, logs={}):
    print "acc %s, loss, %s" % (logs.get('acc'), logs.get('loss'))
history = LossHistory()

for e in range(1000):
  print('Epoch', e)
  # load augmented 'epoch'
  image_batch = []
  mask_batch = []
  image_batch = image_generator.next()
  mask_batch = mask_generator.next()
  # fit the model
  fcn.model.fit(np.array(image_batch), np.array(mask_batch),batch_size=4, verbose=0, callbacks=[history])
  fcn.model.save_weights('data/weights/segmentation%s.h5'%e)

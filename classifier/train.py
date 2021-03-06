# -------------------------------------------
# Train the classifier CNN
# -------------------------------------------
import argparse
import os
import keras
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K
import cnn

cwd = os.path.dirname(__file__)

train_data_dir = './data/train_classifier/train'
validation_data_dir = './data/train_classifier/test'
nb_train_samples = 10000
nb_validation_samples = 500
epochs = 100
batch_size = 64

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--weights", help="weightfile", type=str)
args = parser.parse_args()

# if weights argument is provided, start training from initial state
if args.weights:
	cnn.model.load_weights(args.weights)
 
# callbacks to save weights after each epoch
class Callbacks(keras.callbacks.Callback):
	def on_epoch_end(self, epoch, logs={}):
		self.model.save_weights(os.path.join(cwd, 'data/weights', 'classifier%s.h5' % epoch))
		return
callbacks = Callbacks()

# Image augmentation settings
train_datagen = ImageDataGenerator(
	rescale=1. / 255,
	shear_range=0.2,
	zoom_range=0.2,
	horizontal_flip=True,
	vertical_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

# Data generators, to read from input training directories
train_generator = train_datagen.flow_from_directory(
	train_data_dir,
	target_size=(cnn.img_width, cnn.img_height),
	batch_size=batch_size,
	class_mode='binary')

validation_generator = test_datagen.flow_from_directory(
	validation_data_dir,
	target_size=(cnn.img_width, cnn.img_height),
	batch_size=batch_size,
	class_mode='binary')

# fit the model, with training and validation data generators
cnn.model.fit_generator(
	train_generator,
	steps_per_epoch=nb_train_samples // batch_size,
	epochs=epochs,
	validation_data=validation_generator,
	validation_steps=nb_validation_samples // batch_size,
	class_weight={0:1,1:0.2}, # asymetric class weights to prevent false positives
	callbacks=[callbacks])

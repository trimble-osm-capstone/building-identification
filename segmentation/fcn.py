# -------------------------------------------
# Model for segmentation "U-net" FCN
# -------------------------------------------
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Input, Dropout, UpSampling2D, Concatenate
from keras.models import *
from keras.optimizers import *

img_width, img_height = 256, 256

input_shape = (img_width, img_height, 3)

inputs = Input(input_shape)

# convolution and pooling
conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same')(inputs)
conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same')(conv1)
pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same')(pool1)
conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same')(conv2)
pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same')(pool2)
conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same')(conv3)
pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same')(pool3)
conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same')(conv4)
drop4 = Dropout(0.5)(conv4)
pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same')(pool4)
conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', name='inout')(conv5)
drop5 = Dropout(0.5)(conv5)

# more convolution and upsampling
up6 = Conv2D(512, 2, activation = 'relu', padding = 'same')(UpSampling2D(size = (2,2))(drop5))
merge6 = Concatenate(axis=-1)([drop4,up6]) #concat in from previous layers that have not been pooled and split
conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same')(merge6)
conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same')(conv6)

up7 = Conv2D(256, 2, activation = 'relu', padding = 'same')(UpSampling2D(size = (2,2))(conv6))
merge7 = Concatenate(axis=-1)([conv3,up7])
conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same')(merge7)
conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same')(conv7)

up8 = Conv2D(128, 2, activation = 'relu', padding = 'same')(UpSampling2D(size = (2,2))(conv7))
merge8 = Concatenate(axis=-1)([conv2,up8])
conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same')(merge8)
conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same')(conv8)

up9 = Conv2D(64, 2, activation = 'relu', padding = 'same')(UpSampling2D(size = (2,2))(conv8))
merge9 = Concatenate(axis=-1)([conv1,up9])
conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same')(merge9)
conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same')(conv9)
conv9 = Conv2D(2, 3, activation = 'relu', padding = 'same')(conv9)
conv10 = Conv2D(1, 1, activation = 'sigmoid')(conv9)

model = Model(inputs=inputs, outputs=conv10)
model.compile(optimizer = Adam(lr = 1e-4), loss = 'binary_crossentropy', metrics = ['accuracy'])
import matplotlib.pyplot as plt
import numpy as np

from tensorflow.keras.layers import *
from tensorflow.keras import *
from tensorflow.keras.datasets import mnist
from tensorflow.keras.optimizers import Adam

img_rows = 28
img_cols = 28
channels = 1
img_shape = (img_rows, img_cols, channels)
z_dim = 100

def build_generator(z_dim):
    model = Sequential()

    model.add(Dense(256*7*7, input_dim=z_dim))
    model.add(Reshape((7,7,256)))

    model.add(Conv2DTranspose(128, kernel_size = 3, strides=2, padding = 'same'))
    model.add(BatchNormalization())

    model.add(LeakyReLU(alpha=0.01))

    model.add(Conv2DTranspose(64, kernel_size = 3, strides=1, padding='same'))

    model.add(BatchNormalization())
    model.add(LeakyReLU(alpha=0.01))
    model.add(Conv2DTranspose(1, kernel_size=3, strides=2, padding='same'))
    model.add(Activation('tanh'))

    return model

def build_discriminator(img_shape):
    model = Sequential()
    model.add(Conv2D(32,
                     kernel_size=3,
                     input_shape=img_shape,
                     padding='same'
    ))
    model.add(LeakyReLU(alpha=0.01))
    model.add(Conv2D(64,
                     kernel_size=3,
                     strides=2,
                     padding='same'))
    model.add(LeakyReLU(alpha=0.01))

    model.add(Conv2D(128,
                     kernel_size=3,
                     strides=2,
                     padding='same'))
    model.add(LeakyReLU(alpha=0.01))
    model.add(Flatten())
    model.add(Dense(1, activation='sigmoid'))

    return model


def build_gan(generator, discriminator):
    model = Sequential()

    model.add(generator)
    model.add(discriminator)

    return model

discriminator = build_discriminator(img_shape)
discriminator.compile(loss='binary_crossentropy',
                      optimizer=Adam(),
                      metrics=['accuracy'])

generator = build_generator(z_dim)
discriminator.trainable=False

gan = build_gan(generator, discriminator)
gan.compile(loss='binary_crossentropy', optimizer= Adam())

losses = []
accuracies = []
iteration_checkpoints = []

def train(iterations, batch_size, sample_interval):
    (X_train, _), (_,_) = mnist.load_data()
    X_train = X_train/127.5-1.0
    X_train = np.expand_dims(X_train, axis=3)

    real = np.ones((batch_size,1))
    fake = np.zeros((batch_size,1))

    for iteration in range(iterations):

        idx = np.random.randint(0, X_train.shape[0], batch_size)
        imgs = X_train[idx]

        z = np.random.normal(0,1, (batch_size,100))
        gen_imgs = generator.predict(z)

        d_loss_real = discriminator.train_on_batch(imgs, real)
        d_loss_fake = discriminator.train_on_batch(gen_imgs, fake)
        d_loss, accuracy = 0.5 * np.add(d_loss_real, d_loss_fake)

        g_loss = gan.train_on_batch(z, real)

        if (iteration + 1) % sample_interval == 0:

            losses.append((d_loss, g_loss))
            accuracies.append((100.0 * accuracy))
            iteration_checkpoints.append(iteration + 1)

            print("%d [D 손실 : %f, 정확도: %.2f%%] [G손실 : %f]" % (iteration +1, d_loss, 100.0 *accuracy, g_loss))

            sample_images(generator)

def sample_images(generator, image_grid_rows = 4, image_grid_columns=4):
    z = np.random.normal(0,1, (image_grid_rows * image_grid_columns, z_dim))

    gen_imgs = generator.predict(z)
    gen_imgs = 0.5 *gen_imgs +0.5
    fig, axs = plt.subplots(image_grid_rows,
                            image_grid_columns,
                            figsize=(4,4),
                            sharey=True,
                            sharex=True)

    cnt = 0
    for i in range(image_grid_rows):
        for j in range(image_grid_columns):
            axs[i, j].imshow(gen_imgs[cnt, :, :, 0], cmap='gray')
            axs[i,j].axis('off')
            cnt +=1
    plt.show()


iterations = 2000
batch_size = 128
sample_interval = 1000
train(iterations, batch_size, sample_interval)
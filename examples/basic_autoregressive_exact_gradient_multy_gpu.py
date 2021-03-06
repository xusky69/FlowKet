import tensorflow
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import multi_gpu_model

from flowket.callbacks import TensorBoard
from flowket.callbacks.exact import default_wave_function_callbacks_factory
from flowket.machines import SimpleConvNetAutoregressive1D
from flowket.operators import Ising
from flowket.optimizers import convert_to_accumulate_gradient_optimizer
from flowket.optimization import ExactVariational, loss_for_energy_minimization

hilbert_state_shape = [16, ]
inputs = Input(shape=hilbert_state_shape, dtype='int8')
convnet = SimpleConvNetAutoregressive1D(inputs, depth=7, num_of_channels=32, weights_normalization=False)
orig_model = Model(inputs=inputs, outputs=convnet.predictions)
num_of_gpu = 4
model = multi_gpu_model(orig_model, gpus=num_of_gpu)
model = orig_model
batch_size = 2 ** 12
steps_per_epoch = int(500 * (2 ** 16) // batch_size)

operator = Ising(h=3.0, hilbert_state_shape=hilbert_state_shape, pbc=False)
exact_variational = ExactVariational(model, operator, batch_size)

optimizer = Adam(lr=0.001, beta_1=0.9, beta_2=0.999)
convert_to_accumulate_gradient_optimizer(
    optimizer,
    update_params_frequency=exact_variational.num_of_batch_until_full_cycle,
    accumulate_sum_or_mean=True)
model.compile(optimizer=optimizer, loss=loss_for_energy_minimization)
model.summary()

tensorboard = TensorBoard(log_dir='tensorboard_logs/exact_run_multy_gpu_with_keras')

callbacks = default_wave_function_callbacks_factory(exact_variational,
                                                    true_ground_state_energy=-49.257706531889006, log_in_batch_or_epoch=False) + [tensorboard]
model.fit_generator(exact_variational.to_generator(), steps_per_epoch=steps_per_epoch, epochs=2, callbacks=callbacks, max_queue_size=0,
                    workers=0)
orig_model.save_weights('exact_multy.h5')

import numpy
from tensorflow.keras.callbacks import Callback


class LocalEnergyStats(Callback):
    def __init__(self, generator, validation_generator=None, true_ground_state_energy=None, log_every_batch=True, **kwargs):
        super(LocalEnergyStats, self).__init__(**kwargs)
        self.generator = generator
        self.validation_generator = validation_generator
        self.true_ground_state_energy = true_ground_state_energy
        self.log_every_batch = log_every_batch

    def add_energy_stats_to_logs(self, logs, generator, prefix=""):
        logs['%senergy/energy' % prefix] = numpy.real(generator.current_energy)
        logs['%senergy/local_energy_variance' % prefix] = numpy.real(generator.current_local_energy_variance)
        if self.true_ground_state_energy is not None:
            logs['%senergy/relative_error' % prefix] = (self.true_ground_state_energy - numpy.real(generator.current_energy)) / self.true_ground_state_energy
        

    def on_batch_end(self, batch, logs={}):
        if self.log_every_batch:
            self.add_energy_stats_to_logs(logs, self.generator)
        
    def on_epoch_end(self, batch, logs={}):
        self.add_energy_stats_to_logs(logs, self.generator)
        if self.validation_generator is not None:
            self.add_energy_stats_to_logs(logs, self.validation_generator, prefix='val_')
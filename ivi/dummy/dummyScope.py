"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2012-2017 Alex Forencich
Copyright (c) 2023 IDEX Biometrics Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from .. import ivi
from .. import scope
from .. import scpi

from pathlib import Path

class dummyScope(
    scpi.common.IdnCommand, scpi.common.Reset, scpi.common.Memory,
    scpi.common.SystemSetup, scope.Base, scope.WaveformMeasurement, 
    ivi.Driver
    ):
    """This is a dummy IVI oscilloscope driver designed to be used in testing/simulation
    where there is no access to a real instrument.

    The driver relies on the fact that the base instrument fully defines all methods
    required to implement the driver, they just set/get static variables rather than 
    sending SCPI commands.  This means that setting scope.trigger.type to 'edge' sets
    an attribute of the class but doesn't do any more.

    In order to provide the user some control over what values are read back when taking
    measurements, the class provides the ability to set a callback for each of the 
    defined scope.MeasurementFunction's.
    
    """
 
    def __init__(self, *args, **kwargs):
        
        self._instrument_id = 'dummyScope'
        self._analog_channel_name = list()
        self._analog_channel_count = 2
        self._digital_channel_name = list()
        self._digital_channel_count = 0
        self._channel_count = 2
        self._bandwidth = 1e9

        # Force the use of the pyvisa-sim backend so that no checking is performed
        # on the visa resource identifier.  We don't actually issue any requests to
        # the backend.
        super(dummyScope, self).__init__(
            *args, **kwargs, pyvisa_backend='@sim', prefer_pyvisa=True, cache=False
        )
 
        self._identity_description = "Dummy IVI oscilloscope driver for simulation"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = ""
        self._identity_instrument_manufacturer = ""
        self._identity_instrument_model = ""
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 4
        self._identity_specification_minor_version = 1
        self._identity_supported_instrument_models =['dummyScope']
 
        self.channels._add_property('label',
                        self._get_channel_label,
                        self._set_channel_label)
 
        self._init_channels()
        self._init_callbacks()
 
    def initialize(self, resource = None, id_query = False, reset = False, **keywargs):
        "Opens an I/O session to the instrument."
 
        self._channel_count = self._analog_channel_count + self._digital_channel_count
 
        super(dummyScope, self).initialize(resource, id_query, reset, **keywargs)
 
        # interface clear
        if not self._driver_operation_simulate:
            self._clear()
 
        # check ID
        if id_query and not self._driver_operation_simulate:
            id = self.identity.instrument_model
            id_check = self._instrument_id
            id_short = id[:len(id_check)]
            if id_short != id_check:
                raise Exception("Instrument ID mismatch, expecting %s, got %s", id_check, id_short)
 
        # reset
        if reset:
            self.utility.reset()

    def _init_channels(self):
        try:
            super(dummyScope, self)._init_channels()
        except AttributeError:
            pass

        # Add the channel lable placeholder. Other channel config handled by scope.Base
        self._channel_label = list()

        for i in range(self._analog_channel_count):
            self._channel_label.append("")

    def _init_callbacks(self):
        self._callbacks = dict()
        for measurement_function in scope.MeasurementFunction:
            self._callbacks[measurement_function] = lambda: 0.0

    def set_callback(self, measurement_function, callback):
        assert (callable(callback))
        self._callbacks[measurement_function] = callback
 
    def _load_id_string(self):
        self._identity_instrument_manufacturer = "Dummy"
        self._identity_instrument_model = "dummyScope1234"
        self._identity_instrument_firmware_revision = "0.1"
 
    def _get_identity_instrument_manufacturer(self):
        if self._get_cache_valid():
            return self._identity_instrument_manufacturer
        self._load_id_string()
        return self._identity_instrument_manufacturer
 
    def _get_identity_instrument_model(self):
        if self._get_cache_valid():
            return self._identity_instrument_model
        self._load_id_string()
        return self._identity_instrument_model
 
    def _get_identity_instrument_firmware_revision(self):
        if self._get_cache_valid():
            return self._identity_instrument_firmware_revision
        self._load_id_string()
        return self._identity_instrument_firmware_revision
 
    def _utility_disable(self):
        pass
 
    def _utility_error_query(self):
        error_code = 0
        error_message = "No error"
        return (error_code, error_message)
 
    def _utility_lock_object(self):
        pass
 
    def _utility_reset(self):
        pass

    def _utility_reset_with_defaults(self):
        self._utility_reset()
 
    def _utility_self_test(self):
        code = 0
        message = "Self test passed"
        return (code, message)
 
    def _utility_unlock_object(self):
        pass

    def _get_channel_label(self, index):
        index = ivi.get_index(self._channel_name, index)
        return self._channel_label[index]

    def _set_channel_label(self, index, value):
        value = str(value)
        index = ivi.get_index(self._channel_name, index)
        self._channel_label[index] = value

    def _measurement_fetch_waveform_measurement(self, index, measurement_function):
        index = ivi.get_index(self._channel_name, index)
        if measurement_function not in scope.MeasurementFunction:
            raise ivi.ValueNotSupportedException()
        return self._callbacks[measurement_function]()
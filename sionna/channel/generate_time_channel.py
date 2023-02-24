#
# SPDX-FileCopyrightText: Copyright (c) 2021-2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Class for generating channel responses in the time domain"""


from sionna.channel.utils import cir_to_time_channel

class GenerateTimeChannel:
    # pylint: disable=line-too-long
    r"""GenerateTimeChannel(channel_model, bandwidth, num_time_samples, l_min, l_max, normalize_channel=False)

    Generate channel responses in the time domain.

    For each batch example, ``num_time_samples`` + ``l_max`` - ``l_min`` time steps of a
    channel realization are generated by this layer.
    These can be used to filter a channel input of length ``num_time_samples`` using the
    :class:`~sionna.channel.ApplyTimeChannel` layer.

    The channel taps :math:`\bar{h}_{b,\ell}` (``h_time``) returned by this layer
    are computed assuming a sinc filter is used for pulse shaping and receive filtering.
    Therefore, given a channel impulse response
    :math:`(a_{m}(t), \tau_{m}), 0 \leq m \leq M-1`, generated by the ``channel_model``,
    the channel taps are computed as follows:

    .. math::
        \bar{h}_{b, \ell}
        = \sum_{m=0}^{M-1} a_{m}\left(\frac{b}{W}\right)
            \text{sinc}\left( \ell - W\tau_{m} \right)

    for :math:`\ell` ranging from ``l_min`` to ``l_max``, and where :math:`W` is
    the ``bandwidth``.

    Parameters
    ----------
    channel_model : :class:`~sionna.channel.ChannelModel` object
        An instance of a :class:`~sionna.channel.ChannelModel`, such as
        :class:`~sionna.channel.RayleighBlockFading` or
        :class:`~sionna.channel.tr38901.UMi`.

    bandwidth : float
        Bandwidth (:math:`W`) [Hz]

    num_time_samples : int
        Number of time samples forming the channel input (:math:`N_B`)

    l_min : int
        Smallest time-lag for the discrete complex baseband channel (:math:`L_{\text{min}}`)

    l_max : int
        Largest time-lag for the discrete complex baseband channel (:math:`L_{\text{max}}`)

    normalize_channel : bool
        If set to `True`, the channel is normalized over the block size
        to ensure unit average energy per time step. Defaults to `False`.

    Input
    -----

    batch_size : int
        Batch size. Defaults to `None` for channel models that do not require this paranmeter.

    Output
    -------
    h_time : [batch size, num_rx, num_rx_ant, num_tx, num_tx_ant, num_time_samples + l_max - l_min, l_max - l_min + 1], tf.complex
        Channel responses.
        For each batch example, ``num_time_samples`` + ``l_max`` - ``l_min`` time steps of a
        channel realization are generated by this layer.
        These can be used to filter a channel input of length ``num_time_samples`` using the
        :class:`~sionna.channel.ApplyTimeChannel` layer.
    """

    def __init__(self, channel_model, bandwidth, num_time_samples, l_min, l_max,
                 normalize_channel=False):

        # Callable used to sample channel input responses
        self._cir_sampler = channel_model

        self._l_min = l_min
        self._l_max = l_max
        self._l_tot = l_max - l_min + 1
        self._bandwidth = bandwidth
        self._num_time_steps = num_time_samples
        self._normalize_channel = normalize_channel

    def __call__(self, batch_size=None):

        # Sample channel impulse responses
        # pylint: disable=unbalanced-tuple-unpacking
        h, tau = self._cir_sampler( batch_size,
                                    self._num_time_steps + self._l_tot - 1,
                                    self._bandwidth)

        hm = cir_to_time_channel(self._bandwidth, h, tau, self._l_min,
                                 self._l_max, self._normalize_channel)

        return hm

"""Neural network visual structures for deep learning scenes."""

from __future__ import annotations
import numpy as np
from typing import Sequence, List, Optional
from math_video_engine.objects.base import MObject, VGroup
from math_video_engine.objects.geometry import Circle, Line
from math_video_engine.colors import BLUE, YELLOW, GRAY_D, WHITE, interpolate_color


class NeuralNetworkMObject(VGroup):
    """Visual multi-layer neural network with neurons and synaptic connections."""

    def __init__(
        self,
        layer_sizes: Sequence[int] = (3, 4, 2),
        layer_spacing: float = 3.0,
        neuron_spacing: float = 1.2,
        neuron_radius: float = 0.28,
        neuron_color: str = BLUE,
        synapse_color: str = GRAY_D,
        center: Sequence[float] = (0.0, 0.0),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.layer_sizes = list(layer_sizes)
        self.layer_spacing = layer_spacing
        self.neuron_spacing = neuron_spacing
        self.neuron_radius = neuron_radius
        self.neuron_color = neuron_color
        self.synapse_color = synapse_color
        self.center = np.array(center[:2], dtype=float)

        self.neurons: List[List[Circle]] = []
        self.synapses: List[Line] = []

        self._build_network()

    def _build_network(self) -> None:
        num_layers = len(self.layer_sizes)
        total_width = (num_layers - 1) * self.layer_spacing
        start_x = self.center[0] - total_width / 2.0

        # Construct neurons
        for layer_idx, size in enumerate(self.layer_sizes):
            layer_neurons: List[Circle] = []
            x = start_x + layer_idx * self.layer_spacing
            total_height = (size - 1) * self.neuron_spacing
            start_y = self.center[1] + total_height / 2.0

            for neuron_idx in range(size):
                y = start_y - neuron_idx * self.neuron_spacing
                neuron = Circle(
                    radius=self.neuron_radius,
                    center=(x, y),
                    color=self.neuron_color,
                    stroke_width=2.5,
                    fill_color="#1a2538",
                    fill_opacity=1.0,
                    z_index=2
                )
                layer_neurons.append(neuron)
                self.add(neuron)
            self.neurons.append(layer_neurons)

        # Construct synaptic connections
        for l in range(num_layers - 1):
            curr_layer = self.neurons[l]
            next_layer = self.neurons[l + 1]
            for n1 in curr_layer:
                for n2 in next_layer:
                    syn = Line(
                        start=n1.get_center(),
                        end=n2.get_center(),
                        color=self.synapse_color,
                        stroke_width=1.2,
                        z_index=1
                    )
                    self.synapses.append(syn)
                    self.add(syn)

    def set_layer_activation(self, layer_idx: int, activations: Sequence[float]) -> None:
        """Update neuron brightness based on activation values in [0, 1]."""
        if 0 <= layer_idx < len(self.neurons):
            for neuron, act in zip(self.neurons[layer_idx], activations):
                act_clamped = max(0.0, min(1.0, act))
                color = interpolate_color(self.neuron_color, YELLOW, act_clamped)
                neuron.set_fill(color, opacity=0.3 + 0.7 * act_clamped)

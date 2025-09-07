# utils/generator.py
import numpy as np
from scipy import ndimage
import trimesh
import os
from pathlib import Path

class FunkoChibiGenerator:
    def __init__(self):
        self.tolerance = -0.05
        self.scale = 1.0
        self.character_type = "human"
        self.gender = "male"
        self.pupils = "black"
        self.hair_style = "short"
        self.clothing = None

    def set_tolerance(self, tol):
        self.tolerance = tol

    def create_head(self, scale=1.0):
        """Crear cabeza redondeada estilo chibi"""
        # Esfera básica
        sphere = trimesh.creation.icosphere(radius=0.8 * scale)
        
        # Aplanar ligeramente
        vertices = sphere.vertices
        vertices[:, 1] *= 0.9  # Aplanar verticalmente
        sphere.vertices = vertices
        
        return sphere

    def create_eyes(self, scale=1.0):
        """Ojos blancos + pupilas negras"""
        eye_white = trimesh.creation.icosphere(radius=0.1 * scale)
        eye_white.apply_translation([0.3 * scale, 0.4 * scale, 0])
        
        pupil = trimesh.creation.icosphere(radius=0.06 * scale)
        pupil.apply_translation([0.3 * scale, 0.4 * scale, 0])
        
        return eye_white, pupil

    def create_hair(self, style="short", scale=1.0):
        """Pelo según estilo"""
        if style == "short":
            hair = trimesh.creation.icosphere(radius=0.9 * scale)
            hair.apply_translation([0, 0, 0.1 * scale])
            hair.apply_scale(1.1, 1.0, 1.0)
        elif style == "long":
            hair = trimesh.creation.cylinder(radius=0.7 * scale, height=0.3 * scale)
            hair.apply_translation([0, 0, 0.5 * scale])
            hair.apply_rotation(np.array([0, 0, 0]))
        
        return hair

    def create_torso(self, scale=1.0):
        """Torso cuadrado con redondez"""
        torso = trimesh.creation.box(extents=[0.6 * scale, 0.4 * scale, 0.8 * scale])
        torso.apply_translation([0, 0, 1.2 * scale])
        return torso

    def create_arm(self, side="left", scale=1.0):
        """Brazo cilíndrico"""
        arm = trimesh.creation.cylinder(radius=0.15 * scale, height=1.0 * scale)
        if side == "left":
            arm.apply_translation([-0.5 * scale, 0, 1.2 * scale])
        else:
            arm.apply_translation([0.5 * scale, 0, 1.2 * scale])
        arm.apply_rotation(np.array([0, 0, 0]))
        return arm

    def create_leg(self, side="left", scale=1.0):
        """Pierna cilíndrica"""
        leg = trimesh.creation.cylinder(radius=0.18 * scale, height=1.5 * scale)
        if side == "left":
            leg.apply_translation([-0.25 * scale, 0, 0.3 * scale])
        else:
            leg.apply_translation([0.25 * scale, 0, 0.3 * scale])
        leg.apply_rotation(np.array([0, 0, 0]))
        return leg

    def create_socket(self, radius=0.1, depth=0.1, tolerance=-0.05):
        """Socket de encastre"""
        socket = trimesh.creation.cylinder(radius=radius, height=depth)
        socket.apply_scale(1 + abs(tolerance), 1 + abs(tolerance), 1)
        return socket

    def create_insert(self, radius=0.1, depth=0.12, tolerance=-0.05):
        """Inserto para encajar"""
        insert = trimesh.creation.cylinder(radius=radius + tolerance, height=depth)
        return insert

    def generate_full_model(self):
        """Generar modelo completo"""
        parts = {}
        
        # Cabeza
        parts["head"] = self.create_head(self.scale)
        
        # Ojos
        parts["eye_left"], parts["pupil_left"] = self.create_eyes(self.scale)
        parts["eye_right"], parts["pupil_right"] = self.create_eyes(self.scale)
        parts["eye_right"].apply_translation([0.3 * self.scale, 0.4 * self.scale, 0])
        parts["pupil_right"].apply_translation([0.3 * self.scale, 0.4 * self.scale, 0])
        
        # Pelo
        parts["hair"] = self.create_hair(self.hair_style, self.scale)
        
        # Torso
        parts["torso"] = self.create_torso(self.scale)
        
        # Brazos
        parts["arm_left"] = self.create_arm("left", self.scale)
        parts["arm_right"] = self.create_arm("right", self.scale)
        
        # Piernas
        parts["leg_left"] = self.create_leg("left", self.scale)
        parts["leg_right"] = self.create_leg("right", self.scale)
        
        # Conectores
        parts["neck_socket"] = self.create_socket(0.1 * self.scale, 0.1 * self.scale, self.tolerance)
        parts["neck_insert"] = self.create_insert(0.1 * self.scale, 0.12 * self.scale, self.tolerance)
        
        return parts

    def export_parts(self, output_path, file_format="STL"):
        """Exportar partes a STL u OBJ"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        for name, mesh in self.generate_full_model().items():
            filepath = os.path.join(output_path, f"{name}.{file_format.lower()}")
            if file_format.upper() == "STL":
                mesh.export(filepath, file_type="stl")
            elif file_format.upper() == "OBJ":
                mesh.export(filepath, file_type="obj")

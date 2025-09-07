# utils/generator.py
import numpy as np
import trimesh
import os

class FunkoChibiGenerator:
    def __init__(self):
        self.tolerance = -0.05
        self.scale = 1.0
        self.character_type = "human"
        self.gender = "male"
        self.hair_style = "short"
        self.clothing = None

    def set_tolerance(self, tol):
        self.tolerance = tol

    def create_head(self, scale=1.0):
        """Crear cabeza redondeada estilo chibi"""
        sphere = trimesh.creation.icosphere(subdivisions=2, radius=0.8 * scale)
        # Aplanar ligeramente
        vertices = sphere.vertices.copy()
        vertices[:, 1] *= 0.9  # Aplanar verticalmente
        sphere.vertices = vertices
        return sphere

    def create_eyes(self, side="left", scale=1.0):
        """Ojos blancos + pupilas negras"""
        offset_x = -0.3 * scale if side == "left" else 0.3 * scale
        offset_y = 0.4 * scale
        offset_z = 0.0
        
        # Ojo blanco
        eye_white = trimesh.creation.icosphere(subdivisions=1, radius=0.1 * scale)
        eye_white.apply_translation([offset_x, offset_y, offset_z])
        
        # Pupila
        pupil = trimesh.creation.icosphere(subdivisions=1, radius=0.06 * scale)
        pupil.apply_translation([offset_x, offset_y + 0.02, offset_z])
        
        return eye_white, pupil

    def create_hair(self, style="short", scale=1.0):
        """Pelo según estilo"""
        if style == "short":
            hair = trimesh.creation.icosphere(subdivisions=2, radius=0.85 * scale)
            # Hacerlo ligeramente más alto
            vertices = hair.vertices.copy()
            vertices[:, 2] += 0.1 * scale  # Subir en Z
            hair.vertices = vertices
        elif style == "long":
            # Cilindro para pelo largo
            hair = trimesh.creation.cylinder(radius=0.7 * scale, height=0.3 * scale)
            hair.apply_translation([0, 0, 0.5 * scale])
        else:
            # Sin pelo
            hair = trimesh.Trimesh()
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
        # Rotar para que apunte hacia abajo
        rotation_matrix = trimesh.transformations.rotation_matrix(
            np.pi/2, [1, 0, 0])
        arm.apply_transform(rotation_matrix)
        return arm

    def create_leg(self, side="left", scale=1.0):
        """Pierna cilíndrica"""
        leg = trimesh.creation.cylinder(radius=0.18 * scale, height=1.5 * scale)
        if side == "left":
            leg.apply_translation([-0.25 * scale, 0, 0.3 * scale])
        else:
            leg.apply_translation([0.25 * scale, 0, 0.3 * scale])
        # Rotar para que apunte hacia abajo
        rotation_matrix = trimesh.transformations.rotation_matrix(
            np.pi/2, [1, 0, 0])
        leg.apply_transform(rotation_matrix)
        return leg

    def create_hand(self, side="left", scale=1.0):
        """Mano esférica"""
        hand = trimesh.creation.icosphere(subdivisions=1, radius=0.12 * scale)
        if side == "left":
            hand.apply_translation([-0.5 * scale, 0, 0.2 * scale])
        else:
            hand.apply_translation([0.5 * scale, 0, 0.2 * scale])
        return hand

    def create_foot(self, side="left", scale=1.0):
        """Pie elipsoidal"""
        foot = trimesh.creation.icosphere(subdivisions=1, radius=0.15 * scale)
        # Hacerlo más ancho
        vertices = foot.vertices.copy()
        vertices[:, 1] *= 1.5  # Ancho en Y
        vertices[:, 2] *= 0.5  # Alto en Z
        foot.vertices = vertices
        
        if side == "left":
            foot.apply_translation([-0.25 * scale, 0, -0.8 * scale])
        else:
            foot.apply_translation([0.25 * scale, 0, -0.8 * scale])
        return foot

    def create_socket(self, location, radius=0.1, depth=0.1, tolerance=-0.05):
        """Socket de encastre"""
        socket = trimesh.creation.cylinder(radius=radius - tolerance, height=depth)
        socket.apply_translation(location)
        return socket

    def create_insert(self, location, radius=0.1, depth=0.12, tolerance=-0.05):
        """Inserto para encajar"""
        insert = trimesh.creation.cylinder(radius=radius + tolerance, height=depth)
        insert.apply_translation(location)
        return insert

    def generate_full_model(self):
        """Generar modelo completo"""
        parts = {}
        
        # Cabeza
        parts["head"] = self.create_head(self.scale)
        
        # Ojos
        eye_left, pupil_left = self.create_eyes("left", self.scale)
        eye_right, pupil_right = self.create_eyes("right", self.scale)
        parts["eye_left"] = eye_left
        parts["pupil_left"] = pupil_left
        parts["eye_right"] = eye_right
        parts["pupil_right"] = pupil_right
        
        # Pelo
        if self.hair_style != "none":
            parts["hair"] = self.create_hair(self.hair_style, self.scale)
        
        # Torso
        parts["torso"] = self.create_torso(self.scale)
        
        # Brazos
        parts["arm_left"] = self.create_arm("left", self.scale)
        parts["arm_right"] = self.create_arm("right", self.scale)
        
        # Manos
        parts["hand_left"] = self.create_hand("left", self.scale)
        parts["hand_right"] = self.create_hand("right", self.scale)
        
        # Piernas
        parts["leg_left"] = self.create_leg("left", self.scale)
        parts["leg_right"] = self.create_leg("right", self.scale)
        
        # Pies
        parts["foot_left"] = self.create_foot("left", self.scale)
        parts["foot_right"] = self.create_foot("right", self.scale)
        
        # Conectores - Cuello
        neck_location = [0, 0, 1.8 * self.scale]
        parts["neck_socket"] = self.create_socket(neck_location, 0.1 * self.scale, 0.1 * self.scale, self.tolerance)
        parts["neck_insert"] = self.create_insert(neck_location, 0.1 * self.scale, 0.12 * self.scale, self.tolerance)
        
        # Conectores - Brazos
        arm_locations = [
            [-0.5 * self.scale, 0, 1.2 * self.scale],  # Izquierdo
            [0.5 * self.scale, 0, 1.2 * self.scale]    # Derecho
        ]
        for i, loc in enumerate(arm_locations):
            side = "left" if i == 0 else "right"
            parts[f"arm_socket_{side}"] = self.create_socket(loc, 0.1 * self.scale, 0.1 * self.scale, self.tolerance)
            parts[f"arm_insert_{side}"] = self.create_insert(loc, 0.1 * self.scale, 0.12 * self.scale, self.tolerance)
        
        # Conectores - Piernas
        leg_locations = [
            [-0.25 * self.scale, 0, 0.3 * self.scale],  # Izquierda
            [0.25 * self.scale, 0, 0.3 * self.scale]    # Derecha
        ]
        for i, loc in enumerate(leg_locations):
            side = "left" if i == 0 else "right"
            parts[f"leg_socket_{side}"] = self.create_socket(loc, 0.1 * self.scale, 0.1 * self.scale, self.tolerance)
            parts[f"leg_insert_{side}"] = self.create_insert(loc, 0.1 * self.scale, 0.12 * self.scale, self.tolerance)
        
        return parts

    def export_parts(self, output_path, file_format="STL"):
        """Exportar partes a STL u OBJ"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        parts = self.generate_full_model()
        exported_files = []
        
        for name, mesh in parts.items():
            if len(mesh.vertices) == 0:
                continue  # Saltar partes vacías
                
            filepath = os.path.join(output_path, f"{name}.{file_format.lower()}")
            try:
                if file_format.upper() == "STL":
                    mesh.export(filepath, file_type="stl")
                elif file_format.upper() == "OBJ":
                    mesh.export(filepath, file_type="obj")
                exported_files.append(filepath)
            except Exception as e:
                print(f"Error exporting {name}: {e}")
                
        return exported_files

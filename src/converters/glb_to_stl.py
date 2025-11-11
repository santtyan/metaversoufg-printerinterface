"""Conversor GLB→STL com correção automática de escala para K1 Max"""

import logging
from pathlib import Path
import trimesh

logger = logging.getLogger(__name__)

class GLBToSTLConverter:
    MAX_PRINT_SIZE = 280  # K1 Max bed size with 20mm safety margin
    BED_CENTER = [150, 150, 0]  # K1 Max bed center coordinates
    
    def convert_glb_to_stl(self, glb_path: str) -> str:
        """Converte GLB para STL com correções automáticas"""
        try:
            logger.info(f"Convertendo: {Path(glb_path).name}")
            
            # Load and merge geometries
            mesh = self._load_and_merge(glb_path)
            
            # Apply scale corrections
            mesh = self._fix_scale(mesh)
            mesh = self._fit_to_bed(mesh)
            mesh = self._center_on_bed(mesh)
            
            # Export STL
            return self._export_stl(glb_path, mesh)
            
        except Exception as e:
            logger.error(f"Conversão falhou: {e}")
            return None
    
    def _load_and_merge(self, glb_path: str):
        """Carrega GLB e merge múltiplas geometrias"""
        scene = trimesh.load(glb_path)
        
        if isinstance(scene, trimesh.Scene):
            logger.info(f"GLB contém {len(scene.geometry)} objetos")
            return trimesh.util.concatenate([geom for geom in scene.geometry.values()])
        return scene
    
    def _fix_scale(self, mesh):
        """Corrige escala: metros → milímetros"""
        max_dim = max(mesh.bounds[1] - mesh.bounds[0])
        
        if max_dim < 10:  # Provavelmente em metros
            logger.warning(f"Objeto pequeno ({max_dim:.2f}mm), aplicando escala 1000x")
            mesh.apply_scale(1000.0)
            max_dim = max(mesh.bounds[1] - mesh.bounds[0])
            logger.info(f"Nova dimensão: {max_dim:.1f}mm")
        
        return mesh
    
    def _fit_to_bed(self, mesh):
        """Redimensiona se não couber na mesa"""
        max_dim = max(mesh.bounds[1] - mesh.bounds[0])
        
        if max_dim > self.MAX_PRINT_SIZE:
            scale_factor = self.MAX_PRINT_SIZE / max_dim
            logger.warning(f"Redimensionando: {max_dim:.1f}mm → {self.MAX_PRINT_SIZE}mm")
            mesh.apply_scale(scale_factor)
        
        return mesh
    
    def _center_on_bed(self, mesh):
        """Centraliza objeto na mesa K1 Max"""
        # Move para origem
        center = mesh.bounds.mean(axis=0)
        mesh.apply_translation(-center)
        
        # Move para centro da mesa
        mesh.apply_translation(self.BED_CENTER)
        
        # Base em Z=0
        min_z = mesh.bounds[0][2]
        if min_z != 0:
            mesh.apply_translation([0, 0, -min_z])
        
        logger.info("Objeto centralizado na mesa K1 Max")
        return mesh
    
    def _export_stl(self, glb_path: str, mesh) -> str:
        """Exporta mesh como STL"""
        stl_path = str(glb_path).replace(".glb", ".stl")
        mesh.export(stl_path)
        
        if Path(stl_path).exists():
            size_kb = Path(stl_path).stat().st_size / 1024
            logger.info(f"STL gerado: {Path(stl_path).name} ({size_kb:.1f} KB)")
            return stl_path
        
        logger.error("Falha ao exportar STL")
        return None

# Mantém compatibilidade com interface original
def convert_glb_to_stl(glb_path: str) -> str:
    """Interface compatível com código existente"""
    converter = GLBToSTLConverter()
    return converter.convert_glb_to_stl(glb_path)
"""Conversor GLB->STL usando Trimesh"""

import logging
from pathlib import Path
import trimesh

logger = logging.getLogger(__name__)

def convert_glb_to_stl(glb_path: str) -> str:
    """Converte GLB para STL com correção automática de escala"""
    try:
        logger.info(f"Convertendo GLB->STL: {Path(glb_path).name}")
        scene = trimesh.load(glb_path)
        
        if isinstance(scene, trimesh.Scene):
            logger.info(f"GLB contem {len(scene.geometry)} objetos")
            mesh = trimesh.util.concatenate([
                geom for geom in scene.geometry.values()
            ])
        else:
            mesh = scene
        
        # NOVO: Detectar e corrigir escala
        bounds = mesh.bounds
        max_dimension = max(bounds[1] - bounds[0])
        
        # Etapa 1: Se objeto < 10mm, provavelmente está em metros
        if max_dimension < 10:
            logger.warning(f"⚠ Objeto pequeno detectado ({max_dimension:.2f} unidades)")
            logger.info("✓ Aplicando escala 1000x (metros → milímetros)")
            mesh.apply_scale(1000.0)
            
            # Revalidar dimensões após escala
            max_dimension = max(mesh.bounds[1] - mesh.bounds[0])
            logger.info(f"✓ Nova dimensão: {max_dimension:.1f}mm")
        else:
            logger.info(f"✓ Escala inicial OK ({max_dimension:.1f}mm)")
        
        # Etapa 2: Se objeto > 280mm, redimensionar para caber na mesa (K1 Max = 300mm)
        MAX_PRINT_SIZE = 280  # Margem de segurança de 20mm
        if max_dimension > MAX_PRINT_SIZE:
            scale_factor = MAX_PRINT_SIZE / max_dimension
            logger.warning(f"⚠ Objeto maior que mesa ({max_dimension:.1f}mm > {MAX_PRINT_SIZE}mm)")
            logger.info(f"✓ Redimensionando para {scale_factor*100:.1f}% do tamanho original")
            mesh.apply_scale(scale_factor)
            
            # Revalidar dimensões finais
            final_max = max(mesh.bounds[1] - mesh.bounds[0])
            logger.info(f"✓ Dimensão final: {final_max:.1f}mm (cabe na mesa)")
        
        # Etapa 3: Posicionar no centro da mesa K1 Max (150, 150) e Z=0
        center = mesh.bounds.mean(axis=0)
        mesh.apply_translation(-center)  # Move centro para (0,0,0)
        mesh.apply_translation([150, 150, 0])  # Move para centro da mesa K1 Max
        
        # Colocar base do objeto em Z=0 (no plano de impressão)
        min_z = mesh.bounds[0][2]
        if min_z != 0:
            mesh.apply_translation([0, 0, -min_z])
        
        logger.info(f"✓ Objeto centralizado na origem (0,0,0)")
        
        stl_path = str(glb_path).replace(".glb", ".stl")
        mesh.export(stl_path)
        
        if Path(stl_path).exists():
            size_kb = Path(stl_path).stat().st_size / 1024
            logger.info(f"STL gerado: {Path(stl_path).name} ({size_kb:.1f} KB)")
            return stl_path
        else:
            logger.error("Falha ao exportar STL")
            return None
            
    except Exception as e:
        logger.error(f"Erro na conversao: {e}")
        return None
"""
Wrapper PrusaSlicer CLI com presets Creality
Fatia STL usando valores oficiais da impressora
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from presets.creality_preset_parser import CrealityPresetParser, PrintPreset


@dataclass
class SlicerConfig:
    """ConfiguraÃ§Ã£o para o slicer"""
    printer_model: str = "K1 Max"
    bed_size_x: int = 300
    bed_size_y: int = 300
    bed_size_z: int = 300
    nozzle_diameter: float = 0.4


class PrusaSlicerWrapper:
    """Wrapper para PrusaSlicer CLI usando presets Creality"""
    
    def __init__(
        self,
        prusaslicer_path: str = "prusa-slicer",
        config: Optional[SlicerConfig] = None
    ):
        """
        Args:
            prusaslicer_path: Caminho executÃ¡vel PrusaSlicer
            config: ConfiguraÃ§Ã£o impressora
        """
        self.prusaslicer_path = prusaslicer_path
        self.config = config or SlicerConfig()
        self.preset_parser = CrealityPresetParser()
    
    def _generate_ini_config(self, preset: PrintPreset) -> str:
        """
        Gera arquivo .ini do PrusaSlicer com valores Creality
        
        Args:
            preset: Preset Creality parseado
            
        Returns:
            ConteÃºdo .ini completo
        """
        return f"""# Gerado automaticamente de preset Creality
# Printer: {self.config.printer_model}

[print_settings]
# Camadas
layer_height = {preset.layer_height}
first_layer_height = {preset.initial_layer_height}

# PerÃ­metros e linha de extrusÃ£o
perimeters = 2
top_solid_layers = 4
bottom_solid_layers = 4
first_layer_line_width = 0.42
perimeter_line_width = 0.42

# Infill (baseado no preset Metaverso)
fill_density = 10%
fill_pattern = honeycomb

# Velocidades (mm/s)
perimeter_speed = {preset.print_speed}
infill_speed = {preset.print_speed}
travel_speed = {preset.travel_speed}
first_layer_speed = {preset.initial_layer_speed}

# Suporte (configuraÃ§Ã£o Metaverso)
support_material = 1
support_material_style = tree
support_material_pattern = rectilinear
support_material_spacing = 2.5
support_material_threshold = 0
support_material_auto = 1

# Brim (baseado no preset)
brim_width = 8
brim_type = outer_only

# RetraÃ§Ã£o
retract_length = {preset.retraction_length}
retract_speed = {preset.retraction_speed}

# Skirt
skirts = 1
skirt_distance = 2

[printer_settings]
# Hardware
printer_model = {self.config.printer_model}

bed_shape = 0x0,{self.config.bed_size_x}x0,{self.config.bed_size_x}x{self.config.bed_size_y},0x{self.config.bed_size_y}
max_print_height = {self.config.bed_size_z}
nozzle_diameter = {self.config.nozzle_diameter}

# Limites
max_layer_height = 0.3
min_layer_height = 0.1

[filament_settings]
# Temperaturas
temperature = {preset.nozzle_temp}
first_layer_temperature = {preset.nozzle_temp_initial}
bed_temperature = {preset.bed_temp}
first_layer_bed_temperature = {preset.bed_temp_initial}

# Filament overrides (forÃ§a valores)
filament_temperature = {preset.nozzle_temp}
filament_temperature_0 = {preset.nozzle_temp}
filament_bed_temperature = {preset.bed_temp}
filament_bed_temperature_0 = {preset.bed_temp}

# VentilaÃ§Ã£o
fan_always_on = 1
max_fan_speed = {preset.fan_speed}
min_fan_speed = {preset.fan_speed}

"""
    
    def slice_stl(
        self,
        stl_path: str,
        material: str = "PLA",
        output_path: Optional[str] = None
    ) -> str:
        """
        Fatia arquivo STL usando preset Creality
        
        Args:
            stl_path: Caminho arquivo STL
            material: Material (PLA, ABS, PETG, etc.)
            output_path: Caminho saÃ­da (opcional)
            
        Returns:
            Caminho arquivo G-code gerado
            
        Raises:
            FileNotFoundError: Se STL nÃ£o existe
            RuntimeError: Se slice falhar
        """
        stl_path = Path(stl_path)
        if not stl_path.exists():
            raise FileNotFoundError(f"STL nÃ£o encontrado: {stl_path}")
        
        # Carregar preset Creality
        preset = self.preset_parser.parse_preset(material)
        
        # Gerar config .ini temporÃ¡rio
        config_content = self._generate_ini_config(preset)
        
        # Criar arquivo temporÃ¡rio
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.ini',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(config_content)
            config_file = f.name
        
        # Definir output
        if output_path is None:
            output_path = stl_path.with_suffix('.gcode')
        output_path = Path(output_path)
        
        try:
            # Executar PrusaSlicer
            cmd = [
                self.prusaslicer_path,
                "--export-gcode",
                "--load", config_file,
                "--output", str(output_path),
                str(stl_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300
            )
            
            if not output_path.exists():
                raise RuntimeError(
                    f"G-code nÃ£o foi gerado.\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}"
                )
            
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Erro ao executar PrusaSlicer:\n"
                f"stdout: {e.stdout}\n"
                f"stderr: {e.stderr}"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Timeout ao fatiar (>5min): {stl_path.name}")
        finally:
            # Limpar arquivo temporÃ¡rio
            Path(config_file).unlink(missing_ok=True)


# ========== FUNÃ‡Ã•ES CONVENIENTES ==========

def slice_with_creality_presets(
    stl_path: str,
    material: str = "PLA",
    output_path: Optional[str] = None,
    prusaslicer_path: str = "prusa-slicer"
) -> str:
    """
    Atalho: fatia STL com valores Creality
    
    Args:
        stl_path: Caminho STL
        material: PLA, ABS, PETG, TPU, etc.
        output_path: Caminho saÃ­da (opcional)
        prusaslicer_path: Caminho PrusaSlicer
        
    Returns:
        Caminho G-code gerado
        
    Example:
        >>> gcode = slice_with_creality_presets("model.stl", "PLA")
        >>> print(f"G-code: {gcode}")
    """
    slicer = PrusaSlicerWrapper(prusaslicer_path)
    return slicer.slice_stl(stl_path, material, output_path)

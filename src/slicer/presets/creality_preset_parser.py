"""
Parser de Presets Creality Print
"""
import json
from pathlib import Path
from typing import Dict, Optional, List, Union
from dataclasses import dataclass

@dataclass
class PrintPreset:
    nozzle_temp: int
    nozzle_temp_initial: int
    bed_temp: int
    bed_temp_initial: int
    print_speed: int
    travel_speed: int
    initial_layer_speed: int
    retraction_length: float
    retraction_speed: int
    layer_height: float
    initial_layer_height: float
    infill_density: int
    infill_pattern: str
    support_enabled: bool
    fan_speed: int

class CrealityPresetParser:
    TEMPLATE_BASE = Path("C:/Program Files/Creality/Creality Print 6.2/resources/profiles_template/Template")
    MATERIALS = {
        'PLA': 'filament_pla_template.json',
        'ABS': 'filament_abs_template.json',
        'PETG': 'filament_pet_template.json',
        'TPU': 'filament_tpu_template.json',
        'PA': 'filament_pa_template.json',
        'PC': 'filament_pc_template.json',
        'ASA': 'filament_asa_template.json',
        'HIPS': 'filament_hips_template.json',
        'PVA': 'filament_pva_template.json'
    }
    
    def __init__(self, template_path: Optional[Path] = None):
        self.template_base = template_path or self.TEMPLATE_BASE
        if not self.template_base.exists():
            raise FileNotFoundError(f"Template não encontrado: {self.template_base}")
    
    def _parse_value(self, value: Union[str, int, float, list], target_type: type, default):
        """Parse genérico para string/int/float/lista"""
        if value is None:
            return target_type(default)
        if isinstance(value, list):
            value = value[0] if value else default
        if isinstance(value, str):
            if target_type == int:
                return int(float(value))
            return target_type(value)
        return target_type(value)
    
    def load_raw_preset(self, material: str) -> Dict:
        material_upper = material.upper()
        if material_upper not in self.MATERIALS:
            raise ValueError(f"Material '{material}' não suportado")
        filename = self.MATERIALS[material_upper]
        filepath = self.template_base / "filament" / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_preset(self, material: str) -> PrintPreset:
        raw = self.load_raw_preset(material)
        
        # Parse infill density (remove %)
        infill_raw = raw.get('sparse_infill_density', '15%')
        if isinstance(infill_raw, str):
            infill_density = int(infill_raw.rstrip('%'))
        else:
            infill_density = int(infill_raw)
        
        # Temperaturas com override Metaverso para PLA
        nozzle_temp = self._parse_value(raw.get('nozzle_temperature'), int, 210)
        nozzle_temp_initial = self._parse_value(raw.get('nozzle_temperature_initial_layer'), int, 220)
        
        if material.upper() == 'PLA':
            nozzle_temp = 220
            nozzle_temp_initial = 225
        
        return PrintPreset(
            nozzle_temp=nozzle_temp,
            nozzle_temp_initial=nozzle_temp_initial,
            bed_temp=self._parse_value(raw.get('bed_temperature'), int, 60),
            bed_temp_initial=self._parse_value(raw.get('bed_temperature_initial_layer'), int, 60),
            print_speed=self._parse_value(raw.get('print_speed'), int, 300),
            travel_speed=self._parse_value(raw.get('travel_speed'), int, 500),
            initial_layer_speed=self._parse_value(raw.get('initial_layer_speed'), int, 50),
            retraction_length=self._parse_value(raw.get('retraction_length'), float, 0.4),
            retraction_speed=self._parse_value(raw.get('retraction_speed'), int, 40),
            layer_height=self._parse_value(raw.get('layer_height'), float, 0.2),
            initial_layer_height=self._parse_value(raw.get('initial_layer_height'), float, 0.2),
            infill_density=infill_density,
            infill_pattern=raw.get('sparse_infill_pattern', 'gyroid'),
            support_enabled=bool(int(raw.get('support_enable', 0))),
            fan_speed=self._parse_value(raw.get('fan_max_speed'), int, 100)
        )
    
    def get_temperatures(self, material: str) -> Dict[str, int]:
        preset = self.parse_preset(material)
        return {'nozzle': preset.nozzle_temp, 'bed': preset.bed_temp}
    
    def modify_preset(self, material: str, overrides: Dict) -> Dict:
        preset = self.load_raw_preset(material)
        preset.update(overrides)
        return preset
    
    def list_materials(self) -> List[str]:
        return list(self.MATERIALS.keys())

def get_material_preset(material: str) -> PrintPreset:
    return CrealityPresetParser().parse_preset(material)

def get_nozzle_temp(material: str) -> int:
    return get_material_preset(material).nozzle_temp

def get_bed_temp(material: str) -> int:
    return get_material_preset(material).bed_temp

def get_print_speed(material: str) -> int:
    return get_material_preset(material).print_speed

def get_retraction_settings(material: str) -> Dict[str, float]:
    preset = get_material_preset(material)
    return {'length': preset.retraction_length, 'speed': preset.retraction_speed}

def get_layer_height(material: str) -> float:
    return get_material_preset(material).layer_height

def supports_material(material: str) -> bool:
    try:
        CrealityPresetParser().load_raw_preset(material)
        return True
    except (ValueError, FileNotFoundError):
        return False

if __name__ == "__main__":
    parser = CrealityPresetParser()
    print("=== TESTE PARSER CREALITY ===\n")
    print("1. PLA Preset Completo:")
    pla = parser.parse_preset('PLA')
    print(f"   Nozzle: {pla.nozzle_temp}C")
    print(f"   Bed: {pla.bed_temp}C")
    print(f"   Speed: {pla.print_speed} mm/s")
    print(f"   Layer: {pla.layer_height} mm")
    print(f"   Fan: {pla.fan_speed}%")
    print("\n2. Funcoes Especificas:")
    print(f"   Nozzle PLA: {get_nozzle_temp('PLA')}C")
    print(f"   Bed PETG: {get_bed_temp('PETG')}C")
    print(f"   Supports TPU? {supports_material('TPU')}")
    print("\n3. Materiais Disponiveis:")
    for mat in parser.list_materials():
        temps = parser.get_temperatures(mat)
        print(f"   {mat}: {temps['nozzle']}C / {temps['bed']}C")
    print("\nParser funcional!")

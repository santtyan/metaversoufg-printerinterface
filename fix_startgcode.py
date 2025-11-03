from pathlib import Path

wrapper = Path('src/slicer/prusa_slicer_wrapper.py')
content = wrapper.read_text(encoding='utf-8')

# Remover start_gcode multi-linha quebrado
old_broken = """# Start G-code customizado
start_gcode = M104 S{preset.nozzle_temp_initial}\\nG28\\nG1 Z5 F5000\\nM109 S{preset.nozzle_temp_initial}
bed_shape"""

new_fixed = """bed_shape"""

content = content.replace(old_broken, new_fixed)

# Adicionar start_gcode em LINHA ÚNICA na seção printer
old_section = """[printer_settings]
# Hardware
printer_model = {self.config.printer_model}
bed_shape"""

new_section = """[printer_settings]
# Hardware
printer_model = {self.config.printer_model}
start_gcode = M104 S{preset.nozzle_temp_initial}\\nG28\\nG1 Z5 F5000\\nM109 S{preset.nozzle_temp_initial}
bed_shape"""

if 'start_gcode' not in content:
    content = content.replace(old_section, new_section)
    print('✅ Start G-code CORRIGIDO em linha única')
else:
    print('✅ Já presente')

wrapper.write_text(content, encoding='utf-8')

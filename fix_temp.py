from pathlib import Path

wrapper_file = Path('src/slicer/prusa_slicer_wrapper.py')
content = wrapper_file.read_text(encoding='utf-8')

# Remover start_gcode quebrado
content = content.replace(
    '# Start G-code customizado\nstart_gcode = M104 S{preset.nozzle_temp_initial} ; set temperature\\nG28 ; home all axes\\nG1 Z5 F5000 ; lift nozzle\\nM109 S{preset.nozzle_temp_initial} ; wait for temperature\n',
    ''
)

# Adicionar na seção [printer_settings] com formato correto
old_printer = """[printer_settings]
# Hardware
printer_model = {self.config.printer_model}"""

new_printer = """[printer_settings]
# Hardware
printer_model = {self.config.printer_model}

# Start G-code customizado
start_gcode = M104 S{preset.nozzle_temp_initial}\\nG28\\nG1 Z5 F5000\\nM109 S{preset.nozzle_temp_initial}"""

if 'start_gcode' not in content:
    content = content.replace(old_printer, new_printer)
    
wrapper_file.write_text(content, encoding='utf-8')
print('✅ Start G-code corrigido')

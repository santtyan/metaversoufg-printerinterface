run-batch: 
    python run_pipeline.py
clean:
    Get-ChildItem -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force

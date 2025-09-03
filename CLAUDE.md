# CLAUDE.md - Development Guidelines for Fractal Explorer

## Virtual Environment Usage

**CRITICAL**: Always use the virtual environment for all Python operations.

### Before any Python operations:
```bash
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### Installing packages:
```bash
# ALWAYS activate venv first
source venv/bin/activate
pip install <package_name>

# Update requirements.txt after installing new packages
pip freeze > requirements.txt
```

### Running the application:
```bash
# ALWAYS activate venv first
source venv/bin/activate
python -m fractal_explorer.main
```

### Running tests:
```bash
source venv/bin/activate
python test_app.py
```

## File Structure Maintenance

### Required Project Structure:
```
fractal_explorer/
├── fractals/          # Fractal implementations only
│   ├── __init__.py
│   ├── base.py       # Base classes - DO NOT DELETE
│   ├── escape_time.py # Escape-time fractals
│   ├── ifs.py        # IFS fractals
│   └── lsystem.py    # L-system fractals (if added)
├── rendering/        # Rendering and visualization only
│   ├── __init__.py
│   ├── renderer_2d.py
│   ├── renderer_3d.py # (if 3D support added)
│   └── colormaps.py
├── ui/              # UI components only
│   ├── __init__.py
│   ├── main_window.py
│   ├── controls.py
│   └── canvas.py
├── utils/           # Utility functions only
│   ├── __init__.py
│   ├── math_helpers.py
│   └── performance.py
├── __init__.py      # Package init
├── app.py          # Application class
└── main.py         # Entry point
```

### File Organization Rules:

1. **DO NOT mix concerns**: 
   - Fractal algorithms go in `fractals/`
   - Rendering code goes in `rendering/`
   - UI code goes in `ui/`
   - Helper functions go in `utils/`

2. **DO NOT create duplicate files**:
   - Check if functionality exists before creating new files
   - Extend existing classes rather than creating duplicates

3. **Clean up regularly**:
   - Remove unused imports
   - Delete commented-out code
   - Remove empty or redundant files

## Code Quality Standards

### Before committing code:

1. **Run linting and type checking**:
```bash
source venv/bin/activate
python -m pylint fractal_explorer
python -m mypy fractal_explorer --ignore-missing-imports
```

2. **Format code**:
```bash
source venv/bin/activate
python -m black fractal_explorer --line-length 100
```

3. **Run tests**:
```bash
source venv/bin/activate
python test_app.py
```

## Adding New Features

### When adding a new fractal type:

1. Create the fractal class in the appropriate module:
   - Escape-time fractals → `fractals/escape_time.py`
   - IFS fractals → `fractals/ifs.py`
   - New category → create new module in `fractals/`

2. Inherit from the appropriate base class
3. Update `fractals/__init__.py` to export the new class
4. Add to the fractals dictionary in `ui/main_window.py`

### When adding new UI features:

1. Keep UI logic in `ui/` directory
2. Emit signals for actions, don't directly modify fractal/renderer
3. Update controls in `ui/controls.py`
4. Handle events in `ui/canvas.py` or `ui/main_window.py`

## Performance Guidelines

### Optimization checklist:

1. **Use Numba for compute-intensive functions**:
   - Add `@jit(nopython=True)` decorator
   - Ensure functions are Numba-compatible

2. **Implement progressive rendering**:
   - Start with low resolution
   - Progressively increase detail

3. **Cache computed regions**:
   - Store frequently accessed computations
   - Clear cache on parameter changes

## Dependencies Management

### Adding new dependencies:

```bash
source venv/bin/activate
pip install new_package
pip freeze > requirements.txt
git add requirements.txt
```

### Removing dependencies:

```bash
source venv/bin/activate
pip uninstall package_name
pip freeze > requirements.txt
git add requirements.txt
```

## Common Issues and Solutions

### Import errors:
- **Solution**: Ensure venv is activated: `source venv/bin/activate`

### PyQt5 issues:
- **Solution**: May need system packages: `sudo apt-get install python3-pyqt5` (Linux)

### Numba warnings:
- **Solution**: Can be ignored, or install CUDA toolkit for GPU support

### Performance issues:
- **Solution**: Reduce max_iter, enable progressive rendering, check zoom level

## Testing Checklist

Before pushing changes, ensure:

- [ ] Virtual environment is activated
- [ ] All tests pass: `python test_app.py`
- [ ] Application runs: `python -m fractal_explorer.main`
- [ ] No import errors
- [ ] File structure is maintained
- [ ] requirements.txt is updated if packages changed
- [ ] Code follows the structure guidelines above

## Quick Commands Reference

```bash
# Setup environment (first time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run application
source venv/bin/activate
python -m fractal_explorer.main

# Run tests
source venv/bin/activate
python test_app.py

# Run examples
source venv/bin/activate
python examples/basic_mandelbrot.py
python examples/julia_animation.py

# Update dependencies
source venv/bin/activate
pip freeze > requirements.txt

# Clean up
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
```

## Git Workflow

```bash
# Always ensure venv is in .gitignore
echo "venv/" >> .gitignore

# Before committing
source venv/bin/activate
python test_app.py  # Ensure tests pass
git status          # Review changes
git add -A
git commit -m "Description of changes"
```

## Notes for Future Development

1. **3D Fractals**: Add `renderer_3d.py` in `rendering/` directory
2. **L-Systems**: Add `lsystem.py` in `fractals/` directory  
3. **GPU Support**: Add CUDA kernels in `utils/cuda/` directory
4. **Web Version**: Create separate `web/` directory at root level
5. **Documentation**: Add to `docs/` directory, not in main code directories
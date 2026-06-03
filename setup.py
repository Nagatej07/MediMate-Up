# save as create_structure.py
import os

# Create directories
dirs = [
    'backend', 'frontend/assets', 'src', 'data/input', 
    'data/vector_store', 'data/mongodb_backup', 'tests', 'logs', 'credentials'
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"Created: {d}")

# Create files
files = [
    'backend/__init__.py', 'backend/api.py', 'backend/models.py',
    'backend/dependencies.py', 'backend/requirements.txt', 'backend/run.py',
    'frontend/index.html', 'frontend/styles.css', 'frontend/app.js',
    'requirements.txt', '.gitignore', 'setup.sh', 'README.md'
]

for f in files:
    with open(f, 'w') as file:
        if f.endswith('.html'):
            file.write('<!DOCTYPE html><html><head><title>MediTrack+</title></head><body>Loading...</body></html>')
        elif f.endswith('.css'):
            file.write('body { font-family: Inter, sans-serif; }')
        elif f.endswith('.js'):
            file.write("console.log('MediTrack+ Loaded');")
        elif f == 'requirements.txt':
            file.write('fastapi\nuvicorn\npymongo\ngoogle-cloud-vision\nlangchain\nopenai')
        elif f == '.gitignore':
            file.write('__pycache__/\n.env\ncredentials/*.json\n*.db\n*.log')
        else:
            file.write(f'# {f} created')
    print(f"Created: {f}")

print("\n✅ Project structure created!")
print("\nNext steps:")
print("1. Add your Google Vision JSON to: credentials/google_vision_key.json")
print("2. Edit backend/.env with your credentials")
print("3. Run: pip install -r requirements.txt")
print("4. Run: python backend/run.py")
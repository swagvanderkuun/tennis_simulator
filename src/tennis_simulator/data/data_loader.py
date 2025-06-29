"""
Comprehensive data loader for tennis simulator
Handles both file-based and embedded data sources
"""
import os
import tempfile
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class DataSource:
    """Represents a data source with its content and metadata"""
    content: str
    source_type: str  # 'file' or 'embedded'
    path: str

class DataLoader:
    """Handles loading of data from various sources"""
    
    def __init__(self):
        self.cache = {}  # Cache for loaded data
        self.temp_files = []  # Track temporary files for cleanup
    
    def get_data_source(self, gender: str, data_type: str) -> Optional[DataSource]:
        """Get data source for the specified gender and data type"""
        cache_key = f"{gender}_{data_type}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try file-based loading first
        file_path = self._find_file(gender, data_type)
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                source = DataSource(content=content, source_type='file', path=file_path)
                self.cache[cache_key] = source
                return source
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
        
        # Try embedded data as fallback
        embedded_content = self._get_embedded_data(gender, data_type)
        if embedded_content:
            temp_path = self._create_temp_file(embedded_content, f"{gender}_{data_type}.txt")
            source = DataSource(content=embedded_content, source_type='embedded', path=temp_path)
            self.cache[cache_key] = source
            return source
        
        return None
    
    def _find_file(self, gender: str, data_type: str) -> Optional[str]:
        """Find file path for the specified gender and data type"""
        filename_map = {
            'elo': f'elo_{gender}.txt',
            'yelo': f'yelo_{gender}.txt',
            'form': f'data/elo/yelo_{gender}_form.txt',
            'tier': f'data/elo/tier_{gender}.txt'
        }
        
        filename = filename_map.get(data_type)
        if not filename:
            return None
        
        # Try multiple possible base paths
        possible_paths = [
            os.getcwd(),  # Current working directory
            os.path.join(os.getcwd(), 'data'),  # data subdirectory
            os.path.join(os.getcwd(), 'src', 'tennis_simulator', 'data'),  # src structure
            os.path.dirname(os.path.abspath(__file__)),  # Current file directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'),  # Project root
        ]
        
        # For hosted environments, also try the app directory
        if 'STREAMLIT_SERVER_RUN_ON_SAVE' in os.environ or 'STREAMLIT_SERVER_HEADLESS' in os.environ:
            possible_paths.extend([
                '/app',  # Streamlit Cloud default
                '/home/appuser',  # Alternative Streamlit Cloud path
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'),  # Go up more levels
            ])
        
        for base_path in possible_paths:
            file_path = os.path.join(base_path, filename)
            if os.path.exists(file_path):
                print(f"Found {filename} at: {file_path}")
                return file_path
        
        print(f"Could not find {filename} in any of the following paths:")
        for base_path in possible_paths:
            print(f"  - {base_path}")
        
        return None
    
    def _get_embedded_data(self, gender: str, data_type: str) -> Optional[str]:
        """Get embedded data for the specified gender and data type"""
        try:
            from .embedded_data import get_embedded_data
            return get_embedded_data(gender, data_type)
        except ImportError:
            print("Embedded data module not available")
            return None
    
    def _create_temp_file(self, content: str, suffix: str = '.txt') -> str:
        """Create a temporary file with the given content"""
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        self.temp_files.append(path)
        return path
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Error cleaning up {temp_file}: {e}")
        self.temp_files.clear()

# Global data loader instance
_data_loader = None

def get_data_loader() -> DataLoader:
    """Get the global data loader instance"""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader 
"""
Photo management utilities for OMAC.
"""
import os
import shutil
from typing import List, Optional


class PhotoManager:
    """Manages photo operations for action figures."""
    
    def __init__(self, photos_dir: str):
        self.photos_dir = photos_dir
        os.makedirs(self.photos_dir, exist_ok=True)
    
    def copy_photos_to_collection(self, photo_paths: List[str], figure_id: int) -> List[str]:
        """
        Copy photos to the collection directory with standardized naming.
        
        Args:
            photo_paths: List of source photo file paths
            figure_id: ID of the figure these photos belong to
            
        Returns:
            List of new file paths in the collection directory
        """
        copied_paths = []
        
        for i, photo_path in enumerate(photo_paths):
            if not os.path.exists(photo_path):
                continue
                
            # Create standardized filename
            filename = f"figure_{figure_id}_{i+1}_{os.path.basename(photo_path)}"
            new_path = os.path.join(self.photos_dir, filename)
            
            try:
                shutil.copy2(photo_path, new_path)
                copied_paths.append(new_path)
            except Exception as e:
                print(f"Warning: Could not copy photo {photo_path}: {e}")
                continue
                
        return copied_paths
    
    def delete_photos(self, photo_paths: List[str]) -> None:
        """
        Delete photos from the filesystem.
        
        Args:
            photo_paths: List of photo file paths to delete
        """
        for photo_path in photo_paths:
            if os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except Exception as e:
                    print(f"Warning: Could not delete photo {photo_path}: {e}")
    
    def get_photo_count(self, figure_id: int, db_manager) -> int:
        """
        Get the number of photos for a figure.
        
        Args:
            figure_id: ID of the figure
            db_manager: Database manager instance
            
        Returns:
            Number of photos
        """
        try:
            photos = db_manager.get_figure_photos(figure_id)
            return len(photos)
        except Exception:
            return 0
    
    def validate_photo_paths(self, photo_paths: List[str]) -> List[str]:
        """
        Validate that photo paths exist and are readable.
        
        Args:
            photo_paths: List of photo file paths
            
        Returns:
            List of valid photo paths
        """
        valid_paths = []
        for path in photo_paths:
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    # Try to open the file to ensure it's readable
                    with open(path, 'rb') as f:
                        f.read(1)
                    valid_paths.append(path)
                except Exception:
                    continue
        return valid_paths
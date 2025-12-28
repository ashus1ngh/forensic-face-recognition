"""
Batch Processing for Multiple Suspect Images
"""

import logging
from pathlib import Path
from datetime import datetime
import concurrent.futures
from PyQt5.QtCore import QThread, pyqtSignal

from config.config import BATCH_MAX_IMAGES, BATCH_THREAD_COUNT, BATCH_TIMEOUT
from core.utils import validate_image_file

logger = logging.getLogger(__name__)

class BatchProcessor(QThread):
    """Process multiple suspect images in batch"""
    
    # Signals
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    image_processed = pyqtSignal(str, list)  # image_path, matches
    batch_completed = pyqtSignal(dict)  # results summary
    error_occurred = pyqtSignal(str, str)  # image_path, error_message
    
    def __init__(self, image_paths, db_manager, face_engine):
        super().__init__()
        self.image_paths = image_paths
        self.db = db_manager
        self.face_engine = face_engine
        self.is_cancelled = False
        self.results = []
    
    def run(self):
        """Run batch processing"""
        try:
            total_images = len(self.image_paths)
            processed = 0
            successful = 0
            failed = 0
            total_matches = 0
            
            logger.info(f"Starting batch processing: {total_images} images")
            
            # Process images with thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_THREAD_COUNT) as executor:
                # Submit all tasks
                future_to_path = {
                    executor.submit(self._process_single_image, img_path): img_path 
                    for img_path in self.image_paths
                }
                
                # Process completed tasks
                for future in concurrent.futures.as_completed(future_to_path, timeout=BATCH_TIMEOUT):
                    if self.is_cancelled:
                        logger.info("Batch processing cancelled")
                        break
                    
                    img_path = future_to_path[future]
                    processed += 1
                    
                    try:
                        result = future.result()
                        
                        if result['success']:
                            successful += 1
                            matches = result['matches']
                            total_matches += len(matches)
                            
                            self.results.append({
                                'image_path': img_path,
                                'matches': matches,
                                'match_count': len(matches),
                                'success': True
                            })
                            
                            # Emit signal for this image
                            self.image_processed.emit(img_path, matches)
                            
                            self.progress_updated.emit(
                                processed,
                                total_images,
                                f"Processed: {Path(img_path).name} - {len(matches)} matches found"
                            )
                        else:
                            failed += 1
                            error = result.get('error', 'Unknown error')
                            
                            self.results.append({
                                'image_path': img_path,
                                'error': error,
                                'success': False
                            })
                            
                            self.error_occurred.emit(img_path, error)
                            
                            self.progress_updated.emit(
                                processed,
                                total_images,
                                f"Failed: {Path(img_path).name} - {error}"
                            )
                    
                    except Exception as e:
                        failed += 1
                        error_msg = str(e)
                        logger.error(f"Error processing {img_path}: {e}")
                        
                        self.results.append({
                            'image_path': img_path,
                            'error': error_msg,
                            'success': False
                        })
                        
                        self.error_occurred.emit(img_path, error_msg)
            
            # Emit completion signal
            summary = {
                'total': total_images,
                'processed': processed,
                'successful': successful,
                'failed': failed,
                'total_matches': total_matches,
                'results': self.results,
                'timestamp': datetime.now().isoformat()
            }
            
            self.batch_completed.emit(summary)
            logger.info(f"Batch processing completed: {successful} successful, {failed} failed")
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            self.error_occurred.emit("Batch Process", str(e))
    
    def _process_single_image(self, image_path):
        """
        Process a single image
        
        Returns:
            dict: Processing result
        """
        try:
            # Validate image
            is_valid, message = validate_image_file(image_path)
            if not is_valid:
                return {
                    'success': False,
                    'error': f"Invalid image: {message}"
                }
            
            # Search for matches
            matches = self.face_engine.search_criminal_database(image_path, self.db)
            
            return {
                'success': True,
                'matches': matches,
                'image_path': image_path
            }
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel(self):
        """Cancel batch processing"""
        self.is_cancelled = True
        logger.info("Batch processing cancellation requested")

class BatchResultsManager:
    """Manage and store batch processing results"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def save_batch_results(self, results, user_id):
        """
        Save batch processing results to database
        
        Args:
            results (dict): Batch processing results
            user_id (int): User who ran the batch
        """
        try:
            # For each successful result, save suspect and matches
            for result in results['results']:
                if result['success'] and result.get('matches'):
                    # Save suspect
                    suspect_id = self.db.add_suspect(
                        image_path=result['image_path'],
                        face_encoding=None,  # Would need to extract if required
                        description=f"Batch processed: {results['timestamp']}"
                    )
                    
                    # Save matches
                    for match in result['matches']:
                        self.db.save_match(
                            suspect_id=suspect_id,
                            criminal_id=match['criminal_id'],
                            similarity_score=match['similarity'],
                            notes=f"Batch processing by user {user_id}"
                        )
            
            logger.info(f"Batch results saved: {results['successful']} suspects, {results['total_matches']} matches")
            
        except Exception as e:
            logger.error(f"Error saving batch results: {e}")
    
    def get_batch_statistics(self):
        """Get batch processing statistics"""
        # Could be extended to track batch processing history
        return {
            'total_batches': 0,
            'total_images_processed': 0,
            'average_matches_per_image': 0
        }
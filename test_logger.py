"""
Test script untuk ScraperLogger.
Menguji fungsi logging tanpa melakukan scraping sesungguhnya.
"""

from src.core_logic.logger import ScraperLogger
import time

def test_logger():
    """Test basic logger functionality."""
    print("Testing ScraperLogger...\n")
    
    # Initialize logger
    logger = ScraperLogger()
    
    # Test data
    test_dosen = [
        "Dr. Ahmad Sutanto",
        "Prof. Budi Santoso",
        "Dr. Citra Dewi",
        "Dr. Dedi Rahman",
        "Prof. Eka Wijaya"
    ]
    
    # Start session
    logger.start_session(test_dosen)
    
    # Simulate scraping with success and failures
    logger.log_success("Dr. Ahmad Sutanto", 15, "Profile found successfully")
    time.sleep(0.5)
    
    logger.log_success("Prof. Budi Santoso", 23, "Profile found successfully")
    time.sleep(0.5)
    
    logger.log_failure("Dr. Citra Dewi", "CAPTCHA verification required", "CAPTCHA")
    time.sleep(0.5)
    
    logger.log_success("Dr. Dedi Rahman", 8, "Profile found successfully")
    time.sleep(0.5)
    
    logger.log_failure("Prof. Eka Wijaya", "Profile not found in search results", "PROFILE_NOT_FOUND")
    time.sleep(0.5)
    
    # End session
    summary = logger.end_session()
    
    print("\nTest completed!")
    print(f"Check the logging folder for generated files:")
    print(f"  Folder: {summary['log_dir']}")
    
    return summary

if __name__ == "__main__":
    summary = test_logger()
    print(f"\nFinal Summary:")
    print(f"  Session ID: {summary['session_id']}")
    print(f"  Log Folder: {summary['log_dir']}")
    print(f"  Total: {summary['total']}")
    print(f"  Success: {summary['success']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  CAPTCHA: {summary['captcha']}")

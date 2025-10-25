"""Natural Questions dataset downloader."""

__version__ = "0.1.0"

# Import main classes for easy access
from .downloader import DownloadResult, NQDownloader

__all__ = ["DownloadResult", "NQDownloader", "__version__"]
